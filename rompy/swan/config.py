import logging
import os

from pydantic import validator

from rompy import TEMPLATES_DIR
from rompy.core import (BaseConfig, Coordinate, DataBlob, RompyBaseModel,
                        Spectrum, TimeRange)

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

    def get(self, grid, runtime):
        ret = []
        for forcing in self:
            if forcing[1]:
                logger.info(f"\t processing {forcing[0]} forcing")
                forcing[1]._filter_grid(grid)
                forcing[1]._filter_time(runtime.period)
                ret.append(forcing[1].get(runtime.staging_dir, grid))
        return "\n".join(ret)


class SwanSpectrum(Spectrum):
    @property
    def cmd(self):
        return f"CIRCLE {self.ndirs} {self.fmin} {self.fmax} {self.nfreqs}"


class SwanPhysics(RompyBaseModel):
    friction: str = "MAD"
    friction_coeff: float = 0.1

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

    @property
    def cmd(self):
        ret = ""
        ret += f"GEN3 WESTH 0.000075 0.00175\n"
        ret += f"BREAKING\n"
        ret += f"FRICTION {self.friction} {self.friction_coeff}\n"
        ret += "\n"
        ret += f"TRIADS\n"
        ret += "\n"
        ret += f"PROP BSBT\n"
        ret += f"NUM ACCUR 0.02 0.02 0.02 95 NONSTAT 20\n"
        return ret


class GridOutput(RompyBaseModel):
    """Gridded outputs for SWAN"""

    period: TimeRange | None = None
    variables: list[str] = [
        "DEPTH",
        "UBOT",
        "HSIGN",
        "HSWELL",
        "DIR",
        "TPS",
        "TM01",
        "WIND",
    ]


class SpecOutput(RompyBaseModel):
    """Spectral outputs for SWAN"""

    period: TimeRange | None = None
    locations: OutputLocs | None = None


class Outputs(RompyBaseModel):
    """Outputs for SWAN"""

    grid: GridOutput = GridOutput()
    spec: SpecOutput = SpecOutput()
    _datefmt: str = "%Y%m%d.%H%M%S"

    @property
    def cmd(self):
        out_intvl = "1.0 HR"  # Hardcoded for now, need to get from time object too
        frequency = "0.25 HR"  # Hardcoded for now, need to get from time object too
        ret = "OUTPUT OPTIONS BLOCK 8\n"
        ret += f"BLOCK 'COMPGRID' HEADER 'outputs/swan_out.nc' LAYOUT 1 {' '.join(self.grid.variables)} OUT {self.grid.period.start.strftime(self._datefmt)} {out_intvl}\n"
        ret += "\n"
        ret += f"POINTs 'pts' FILE 'out.loc'\n"
        ret += f"SPECout 'pts' SPEC2D ABS 'outputs/spec_out.nc' OUTPUT {self.spec.period.start.strftime(self._datefmt)} {out_intvl}\n"
        ret += f"TABle 'pts' HEADer 'outputs/tab_out.nc' TIME XP YP HS TPS TM01 DIR DSPR WIND OUTPUT {self.grid.period.start.strftime(self._datefmt)} {out_intvl}\n"
        return ret


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

    grid: SwanGrid = SwanGrid(
        x0=115.68, y0=-32.76, dx=0.001, dy=0.001, nx=390, ny=150, rot=77
    )
    spectral_resolution: SwanSpectrum = SwanSpectrum()
    forcing: ForcingData = ForcingData()
    physics: SwanPhysics = SwanPhysics()
    output_locs: OutputLocs = OutputLocs()
    outputs: Outputs = Outputs()
    spectra_file: str = "boundary.spec"
    _datefmt: str = "%Y%m%d.%H%M%S"
    # subnests: list[SwanConfig] = []

    @property
    def domain(self):
        output = f"CGRID {self.grid.cgrid} {self.spectral_resolution.cmd}\n"
        output += f"{self.grid.cgrid_read}\n"
        return output

    def _get_grid(self, key=None):
        from intake.source.utils import reverse_format

        grid_spec = self.bottom_grid
        fmt = "{gridtype} {x0:f} {y0:f} {rot:f} {nx:d} {ny:d} {dx:f} {dy:f}"
        if "EXC" in grid_spec:  # append excluded value string
            fmt += " EXC {exc:f}"
        grid_params = reverse_format(fmt, grid_spec)
        return SwanGrid(**grid_params)

    def __call__(self, runtime) -> str:
        ret = {}
        if not self.outputs.grid.period:
            self.outputs.grid.period = runtime.period
        if not self.outputs.spec.period:
            self.outputs.spec.period = runtime.period
        out_intvl = "1.0 HR"  # Hardcoded for now, need to get from time object too
        frequency = "0.25 HR"  # Hardcoded for now, need to get from time object too
        ret["grid"] = f"{self.domain}"
        ret["forcing"] = self.forcing.get(self.grid, runtime)
        ret["physics"] = f"{self.physics.cmd}"
        ret["remaining"] = f"BOUND NEST '{self.spectra_file}' CLOSED\n"
        ret["outputs"] = self.outputs.cmd
        ret["output_locs"] = self.output_locs
        return ret
