import logging
import os
import platform
from datetime import datetime

from pydantic import validator

from rompy import TEMPLATES_DIR
from rompy.core import (BaseConfig, Coordinate, DataBlob, RompyBaseModel,
                        TimeRange)

from .data import SwanDataGrid
from .grid import SwanGrid

logger = logging.getLogger(__name__)


class OutputLocs(RompyBaseModel):
    """Output locations for SWAN

    Parameters
    ----------
    coords : list[Coordinate]
        list of coordinates to output spectra
    """

    coords: list[Coordinate] = [["115.61", "-32.618"], ["115.686067", "-32.532381"]]

    def __repr__(self):
        ret = __class__.__name__ + "\n"
        for coord in self.coords:
            ret += f"  {coord[0]} {coord[1]}\n"
        return ret


class ForcingData(RompyBaseModel):
    bottom: SwanDataGrid | None = None  # TODO Raf should probably be required?
    wind: SwanDataGrid | None = None
    current: SwanDataGrid | None = None
    boundary: SwanDataGrid | None = None


class SwanConfig(BaseConfig):
    """SWAN configuration

    Parameters
    ----------
    template : str
        Path to template file. If this is a git repository, the template will be cloned by cookiecutter.
    out_start : datetime. If not provided, will be set to compute_start
    out_intvl : str
        Output interval. Must be in the format "1.0 HR" or "1.0 DY"
    output_locs : OutputLocs
        List of coordinates to output spectra
    wind_grid : str TODO clean up these definitions
        Grid definition for wind output
    wind_read : str
        Grid definition for wind input
    bottom_grid : str
        Grid definition for bathymetry output
    bottom_file : str
        Path to bathymetry file
    friction : str
        Friction type. Must be one of MAD, OTHER or ANDANOTHER
    friction_coeff : str
        Friction coefficient. Must be between 0 and 1
    spectra_file : str
        Path to input boundary spectra file
    """

    template: str = os.path.join(TEMPLATES_DIR, "swan")
    cgrid: SwanGrid = SwanGrid(
        x0=115.68, y0=-32.76, dx=0.001, dy=0.001, nx=390, ny=150, rot=77
    )
    out_period: TimeRange | None = None
    forcing: ForcingData = ForcingData()
    output_locs: OutputLocs = OutputLocs()
    friction: str = "MAD"
    friction_coeff: str = "0.1"
    spectra_file: str = "boundary.spec"
    _datefmt: str = "%Y%m%d.%H%M%S"
    # subnests: list[SwanConfig] = []

    @validator("friction")
    def validate_friction(cls, v):
        if v not in ["MAD", "OTHER", "ANDANOTHER"]:
            raise ValueError(
                "friction must be one of MAD, OTHER or ANDANOTHER"
            )  # TODO Raf to add actual friction options
        return v

    @validator("friction_coeff")
    def validate_friction_coeff(cls, v):
        # TODO Raf to add sensible friction coeff range
        if float(v) > 1:
            raise ValueError("friction_coeff must be less than 1")
        if float(v) < 0:
            raise ValueError("friction_coeff must be greater than 0")
        return v

    def _get_grid(self, key=None):
        from intake.source.utils import reverse_format

        grid_spec = self.bottom_grid
        fmt = "{gridtype} {x0:f} {y0:f} {rot:f} {nx:d} {ny:d} {dx:f} {dy:f}"
        if "EXC" in grid_spec:  # append excluded value string
            fmt += " EXC {exc:f}"
        grid_params = reverse_format(fmt, grid_spec)
        return SwanGrid(**grid_params)

    def generate(self, runtime) -> str:
        """Generate SWAN input file

        Parameters
        ----------
        run_dir : str
            Path to run directory
        """

        return output

    def __call__(self, runtime) -> str:
        ret = {}
        if not self.out_period:
            self.out_period = runtime.period
        out_intvl = "1.0 HR"  # Hardcoded for now, need to get from time object too
        frequency = "0.25 HR"  # Hardcoded for now, need to get from time object too
        ret["grid"] = f"CGRID {self.cgrid.cgrid} CIRCLE 36 0.0464 1. 31\n"
        ret["grid"] += f"{self.cgrid.cgrid_read}\n"
        ret["grid"] += "\n"
        for forcing in self.forcing:
            if forcing[1]:
                logger.info(f"\t processing {forcing[0]} forcing")
                forcing[1]._filter_grid(self.cgrid)
                forcing[1]._filter_time(runtime.period)
                ret["grid"] += forcing[1].get(runtime.staging_dir, self.cgrid)
                ret["grid"] += "\n"
        ret["grid"] += f"GEN3 WESTH 0.000075 0.00175\n"
        ret["grid"] += f"BREAKING\n"
        ret["grid"] += f"FRICTION {self.friction} {self.friction_coeff}\n"
        ret["grid"] += "\n"
        ret["grid"] += f"TRIADS\n"
        ret["grid"] += "\n"
        ret["grid"] += f"PROP BSBT\n"
        ret["grid"] += f"NUM ACCUR 0.02 0.02 0.02 95 NONSTAT 20\n"
        ret["grid"] += "\n"
        ret["grid"] += f"BOUND NEST '{self.spectra_file}' CLOSED\n"
        ret["grid"] += "\n"
        ret["grid"] += f"OUTPUT OPTIONS BLOCK 8\n"
        ret[
            "grid"
        ] += f"BLOCK 'COMPGRID' HEADER 'outputs/swan_out.nc' LAYOUT 1 DEPTH UBOT HSIGN HSWELL DIR TPS TM01 WIND OUT {self.out_period.start.strftime(self._datefmt)} {out_intvl}\n"
        ret["grid"] += "\n"
        ret["grid"] += f"POINTs 'pts' FILE 'out.loc'\n"
        ret[
            "grid"
        ] += f"SPECout 'pts' SPEC2D ABS 'outputs/spec_out.nc' OUTPUT {self.out_period.start.strftime(self._datefmt)} {out_intvl}\n"
        ret[
            "grid"
        ] += f"TABle 'pts' HEADer 'outputs/tab_out.nc' TIME XP YP HS TPS TM01 DIR DSPR WIND OUTPUT {self.out_period.start.strftime(self._datefmt)} {out_intvl}\n"
        ret["grid"] += "\n"
        ret[
            "grid"
        ] += f"COMPUTE NONST {runtime.period.start.strftime(self._datefmt)} {frequency} {runtime.period.end.strftime(self._datefmt)}\n"
        ret["grid"] += "\n"
        ret["grid"] += f"STOP\n"
        ret["output_locs"] = self.output_locs
        return ret
