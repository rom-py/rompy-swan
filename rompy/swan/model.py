import logging

import numpy as np
import xarray as xr

from rompy.core import BaseGrid, BaseModel

from .config import SwanConfig

logger = logging.getLogger(__name__)


class SwanModel(BaseModel):
    model: str = "SWAN"
    config: SwanConfig = SwanConfig()

    def __init__(self, **data):
        super().__init__(**data)

        # if grid start is not set, set to compute_start
        if not self.config.out_start:
            self.config.out_start = self.compute_start

    # @property
    # def subnests(self):
    #     """Process subnests for SWAN
    #
    #     Just a proposal for now. Provides an elegant way of initilising subnests
    #     """
    #     ii = 1
    #     subnests = []
    #     for config in self.config.subnests:
    #         self.reinit(
    #             instance=self, run_id=f"{self.run_id}_subnest{ii}", config=config
    #         )
    #         ii += 1
    #     return subnests

    @classmethod
    def reinit(cls, instance, run_id, **kwargs):
        """Re-initialise a model with the same configuration

        Parameters
        ----------
        run_id : str
            run_id of the previous run
        **kwargs
            Any additional keyword arguments to pass to the model initialisation

        Returns
        -------
        SwanModel
            A new model instance
        """
        kwg = instance.dict()
        kwg.pop("run_id")
        kwg.update(kwargs)
        model = cls(run_id=run_id, **kwg)
        return model

    # def generate(self):
    #     """Generate SWAN input files"""
    #     super().generate()
    #     for nest in self.subnests:
    #         nest.generate()


@xr.register_dataset_accessor("swan")
class Swan_accessor(object):
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def to_inpgrid(
        self,
        output_file,
        grid=None,
        var="WIND",
        fmt="%.2f",
        x="lon",
        y="lat",
        z1="u10",
        z2=None,
        time="time",
    ):
        """This function writes to a SWAN inpgrid format file (i.e. WIND)

        Args:
        TBD
        """
        import os

        import numpy as np
        import pandas as pd

        ds = self._obj

        if grid is None:
            # If no grid passed in assume it is a REG grid
            if len(ds[x].shape) == 1:
                grid = SwanGrid(
                    gridtype="REG",
                    x0=float(ds[x].min()),
                    y0=float(ds[y].min()),
                    dx=float(np.diff(ds[x]).mean()),
                    dy=float(np.diff(ds[y]).mean()),
                    nx=len(ds[x]),
                    ny=len(ds[y]),
                    rot=0,
                )
            else:
                raise ValueError(
                    "No grid specified for output and number of dims for x-coordinate > 1"
                )
        # else:
        #     raise NotImplementedError('Specifying an alternative output grid is currently not implemented. Only regular grids supported.')

        # ds = ds.transpose((time,) + ds[x].dims)
        dt = np.diff(ds.time.values).mean() / pd.to_timedelta(1, "H")

        inptimes = []
        with open(output_file, "wt") as f:
            # iterate through time
            for ti, windtime in enumerate(ds.time.values):
                time_str = pd.to_datetime(windtime).strftime("%Y%m%d.%H%M%S")
                logger.debug(time_str)

                # write SWAN time header to file:
                f.write(f"{time_str}\n")

                # Write first component to file
                z1t = np.squeeze(ds[z1].isel(time=ti).values)
                np.savetxt(f, z1t, fmt=fmt)

                if z2 is not None:
                    z2t = np.squeeze(ds[z2].isel(time=ti).values)
                    np.savetxt(f, z2t, fmt=fmt)

                inptimes.append(time_str)

        if len(inptimes) < 1:
            import os

            os.remove(output_file)
            raise ValueError(
                f"***Error! No times written to {output_file}\n. Check the input data!"
            )

        input_strings = (
            f"{grid.inpgrid} NONSTATION {inptimes[0]} {dt} HR",
            f"1 '{os.path.basename(output_file)}' 3 0 1 0 FREE",
        )

        return input_strings

    def to_tpar_boundary(
        self,
        dest_path,
        boundary,
        interval,
        x_var="lon",
        y_var="lat",
        hs_var="sig_wav_ht",
        per_var="pk_wav_per",
        dir_var="pk_wav_dir",
        dir_spread=20.0,
    ):
        """This function writes parametric boundary forcing to a set of
        TPAR files at a given distance based on gridded wave output. It returns the string to be included in the Swan INPUT file.

        At present simple nearest neighbour point lookup is used.

        Args:
        TBD
        """
        from shapely.ops import substring

        bound_string = "BOUNDSPEC SEGM XY "
        point_string = "&\n {xp:0.8f} {yp:0.8f} "
        file_string = "&\n {len:0.8f} '{fname}' 1 "

        for xp, yp in boundary.exterior.coords:
            bound_string += point_string.format(xp=xp, yp=yp)

        bound_string += "&\n VAR FILE "

        n_pts = int((boundary.length) / interval)
        splits = np.linspace(0, 1.0, n_pts)
        boundary_points = []
        j = 0
        for i in range(len(splits) - 1):
            segment = substring(
                boundary.exterior, splits[i], splits[i + 1], normalized=True
            )
            xp = segment.coords[1][0]
            yp = segment.coords[1][1]
            logger.debug(f"Extracting point: {xp},{yp}")
            ds_point = self._obj.sel(
                indexers={x_var: xp, y_var: yp}, method="nearest", tolerance=interval
            )
            if len(ds_point.time) == len(self._obj.time):
                if not np.any(np.isnan(ds_point[hs_var])):
                    with open(f"{dest_path}/{j}.TPAR", "wt") as f:
                        f.write("TPAR\n")
                        for t in range(len(ds_point.time)):
                            ds_row = ds_point.isel(time=t)
                            lf = "{tt} {hs:0.2f} {per:0.2f} {dirn:0.1f} {spr:0.2f}\n"
                            f.write(
                                lf.format(
                                    tt=str(
                                        ds_row["time"]
                                        .dt.strftime("%Y%m%d.%H%M%S")
                                        .values
                                    ),
                                    hs=float(ds_row[hs_var]),
                                    per=float(ds_row[per_var]),
                                    dirn=float(ds_row[dir_var]),
                                    spr=dir_spread,
                                )
                            )
                    bound_string += file_string.format(
                        len=splits[i + 1] * boundary.length, fname=f"{j}.TPAR"
                    )
                    j += 1

        return bound_string
