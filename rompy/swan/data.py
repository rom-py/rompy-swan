import logging
import os

import numpy as np
import xarray as xr
from pydantic import root_validator

from rompy.core import DataGrid

from .grid import SwanGrid

logger = logging.getLogger(__name__)

FILL_VALUE = -99.0


class SwanDataGrid(DataGrid):
    """This class is used to write SWAN data from a dataset.

    Parameters
    ----------
    path: str
            Optional local file path
    url: str
            Optional remote file url
    catalog: str
            Optional intake catalog
    dataset: str
            Optional intake dataset id
    params: dict
            Optional parameters to pass to the intake catalog
    filter: Filter
            Optional filter specification to apply to the dataset
    xarray_kwargs: dict
            Optional keyword arguments to pass to xarray.open_dataset
    netcdf_kwargs: dict
            Optional keyword arguments to pass to xarray.Dataset.to_netcdf
    var: str
            Variable name to write


    """

    z1: str
    z2: str = None
    var: str = "WIND"

    # root validator
    @root_validator
    def ensure_z1_in_data_vars(cls, values):
        params = values.get("params")
        data_vars = params.get("data_vars", [])
        for z in [values.get("z1"), values.get("z2")]:
            if z and z not in data_vars:
                logger.debug(f"Adding {z} to data_vars")
                data_vars.append(z)
        values["params"]["data_vars"] = data_vars
        return values

    def get(self, staging_dir: str, grid: SwanGrid = None):
        output_file = os.path.join(staging_dir, f"{self.id}.grd")
        logger.info(f"\tWriting {self.id} to {output_file}")
        inpwind, readwind = self.ds.swan.to_inpgrid(
            output_file=output_file,
            z1=self.z1,
            z2=self.z2,
            grid=grid,
            var=self.var,
        )
        output = f"INPGRID {self.var} {inpwind}\n"
        output += f"READINP {self.var} {readwind}\n"
        return output


@xr.register_dataset_accessor("swan")
class Swan_accessor(object):
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def grid(self, x="lon", y="lat", exc=FILL_VALUE):
        """SWAN Grid object for this dataset.

        TODO: Perhaps we could assume y, x are the last 2 axes.

        """
        return SwanGrid(
            gridtype="REG",
            x0=float(self._obj[x].min()),
            y0=float(self._obj[y].min()),
            dx=float(np.diff(self._obj[x]).mean()),
            dy=float(np.diff(self._obj[y]).mean()),
            nx=len(self._obj[x]),
            ny=len(self._obj[y]),
            rot=0,
            exc=exc,
        )

    def to_bottom_grid(
        self,
        output_file,
        fmt="%4.2f",
        x="lon",
        y="lat",
        z="depth",
        vmin=0.0,
        fill_value=FILL_VALUE,
        fac=1.0,
    ):
        """Write SWAN inpgrid BOTTOM file.

        Parameters
        ----------
        output_file: str
            Local file name for the ascii output file.
        fmt: str
            String float formatter.
        x: str
            Name of the x-axis in the dataset.
        y: str
            Name of the y-axis in the dataset.
        z: str
            Name of the bottom variable in the dataset.
        vmin: float
            Minimum value below which depths are masked.
        fill_value: float
            Fill value.
        fac: float
            Multiplying factor, only necessary when the data are not in meters.

        Returns
        -------
        inpgrid: str
            SWAN INPgrid command instruction.
        readinp: str
            SWAN READinp command instruction.

        TODO: Merge this method with `to_inpgrid`.
        TODO: Change cookiecutter so readinp is used.

        """
        dset_to_swan(
            dset=self._obj.where(self._obj > vmin).transpose(..., y, x),
            output_file=output_file,
            fmt=fmt,
            variables=[z],
            fill_value=fill_value,
        )
        grid = self.grid(x=x, y=y)
        inpgrid = f"{grid.inpgrid}"
        readinp = f"{fac} '{Path(output_file).name}' 3 FREE"
        return inpgrid, readinp

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
