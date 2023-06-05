import logging
from typing import Optional

from pydantic import Field, validator
from typing_extensions import Literal

from rompy.core import BaseConfig, Coordinate, RompyBaseModel, Spectrum, TimeRange

from .data import SwanDataGrid
from .grid import SwanGrid

logger = logging.getLogger(__name__)


class OutputLocs(RompyBaseModel):
    """Output locations"""

    coords: list[Coordinate] = Field(
        [], description="list of coordinates to output spectra"
    )
    # coords: list[Coordinate] = [["115.61", "-32.618"], ["115.686067", "-32.532381"]]

    def __repr__(self):
        ret = __class__.__name__ + "\n"
        for coord in self.coords:
            ret += f"  {coord[0]} {coord[1]}\n"
        return ret

    def __str__(self):
        ret = ""
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

    def __str__(self):
        ret = ""
        for forcing in self:
            if forcing[1]:
                ret += f"{forcing[0]}:"
                if forcing[1].url:
                    ret += f" {forcing[1].url}\n"
                if forcing[1].path:
                    ret += f" {forcing[1].path}\n"
                if forcing[1].catalog:
                    ret += f" {forcing[1].catalog}"
                    ret += f" {forcing[1].dataset}\n"
        return ret


class SwanSpectrum(Spectrum):
    """SWAN Spectrum"""

    @property
    def cmd(self):
        return f"CIRCLE {self.ndirs} {self.fmin} {self.fmax} {self.nfreqs}"


class SwanPhysics(RompyBaseModel):
    """Container class represting configuraable SWAN physics options"""

    friction: str = Field(
        default="MAD", description="The type of friction, either 'MAD' or 'TODO'."
    )
    friction_coeff: float = Field(
        default=0.1,
        description="The coefficient of friction for the given surface and object.",
    )

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

    def __str__(self):
        ret = "\tGrid:\n"
        if self.period:
            ret += f"\t\tperiod: {self.period}\n"
        ret += f"\t\tvariables: {' '.join(self.variables)}\n"
        return ret


class SpecOutput(RompyBaseModel):
    """Spectral outputs for SWAN"""

    period: TimeRange | None = None
    locations: OutputLocs = OutputLocs(coords=[])  # TODO change to None

    def __str__(self):
        ret = "\tSpec\n"
        if self.period:
            ret += f"\t\tperiod: {self.period}\n"
        ret += f"\t\tlocations: {self.locations}\n"
        return ret


class SpecOutput(RompyBaseModel):
    period: Optional[TimeRange] = Field(
        None, description="Time range for which the spectral outputs are requested"
    )
    locations: Optional[OutputLocs] = Field(
        OutputLocs(coords=[]),
        description="Output locations for which the spectral outputs are requested",
    )

    def __str__(self):
        ret = "\tSpec\n"
        if self.period:
            ret += f"\t\tperiod: {self.period}\n"
        ret += f"\t\tlocations: {self.locations}\n"
        return ret


class Outputs(RompyBaseModel):
    """Outputs for SWAN"""

    grid: GridOutput = GridOutput()
    spec: SpecOutput = SpecOutput()
    _datefmt: str = "%Y%m%d.%H%M%S"

    @property
    def cmd(self):
        out_intvl = "1.0 HR"  # Hardcoded for now, need to get from time object too TODO
        ret = "OUTPUT OPTIONS BLOCK 8\n"
        ret += f"BLOCK 'COMPGRID' HEADER 'outputs/swan_out.nc' LAYOUT 1 {' '.join(self.grid.variables)} OUT {self.grid.period.start.strftime(self._datefmt)} {out_intvl}\n"
        ret += "\n"
        if self.spec.locations:
            ret += f"POINTs 'pts' FILE 'out.loc'\n"
        ret += f"SPECout 'pts' SPEC2D ABS 'outputs/spec_out.nc' OUTPUT {self.spec.period.start.strftime(self._datefmt)} {out_intvl}\n"
        ret += f"TABle 'pts' HEADer 'outputs/tab_out.nc' TIME XP YP HS TPS TM01 DIR DSPR WIND OUTPUT {self.grid.period.start.strftime(self._datefmt)} {out_intvl}\n"
        return ret

    def __str__(self):
        ret = "Outputs:\n"
        ret += f"{self.grid}"
        ret += f"{self.spec}"
        return ret


class SwanConfig(BaseConfig):
    """SWAN configuration

    Parameters
    ----------
    grid : SwanGrid
        Grid for SWAN
    spectral_resolution : SwanSpectrum
        Spectral resolution for SWAN
    forcing : ForcingData
        Forcing data for SWAN
    physics : SwanPhysics
        Physics options for SWAN
    outputs : Outputs
        Outputs for SWAN
    """

    grid: SwanGrid
    model_type: Literal["swan"] = "swan"
    spectral_resolution: SwanSpectrum = SwanSpectrum()
    forcing: ForcingData = ForcingData()
    physics: SwanPhysics = SwanPhysics()
    outputs: Outputs = Outputs()
    spectra_file: str = "boundary.spec"
    template: str = "/source/rompy/rompy/templates/swan"
    _datefmt: str = "%Y%m%d.%H%M%S"
    # subnests: list[SwanConfig] = []

    @property
    def domain(self):
        output = f"CGRID {self.grid.cgrid} {self.spectral_resolution.cmd}\n"
        output += f"{self.grid.cgrid_read}\n"
        return output

    def _get_grid(self, key=None):
        # TODO - Is this functionality needed?
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
        ret["grid"] = f"{self.domain}"
        ret["forcing"] = self.forcing.get(self.grid, runtime)
        ret["physics"] = f"{self.physics.cmd}"
        # TODO raf to complete boundary bit
        ret["remaining"] = f"BOUND NEST '{self.spectra_file}' CLOSED\n"
        ret["outputs"] = self.outputs.cmd
        ret["output_locs"] = self.outputs.spec.locations
        return ret

    def __str__(self):
        ret = f"grid: {self.grid}\n"
        ret += f"spectral_resolution: {self.spectral_resolution}\n"
        ret += f"forcing: {self.forcing}\n"
        ret += f"physics: {self.physics}\n"
        ret += f"outputs: {self.outputs}\n"
        return ret
