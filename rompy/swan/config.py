import logging
from pathlib import Path

from pydantic import validator

from rompy.core import BaseConfig, Coordinate, RompyBaseModel, Spectrum, TimeRange
from rompy.core.render import render
from rompy.swan.components import cgrid, inpgrid

from .data import SwanDataGrid
from .grid import SwanGrid

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
COMPONENTS = {
    "cgrid": cgrid.REGULAR | cgrid.CURVILINEAR | cgrid.UNSTRUCTURED,
    "inpgrid": list[inpgrid.REGULAR | inpgrid.CURVILINEAR | inpgrid.UNSTRUCTURED],
}


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
    locations: OutputLocs | None = OutputLocs()  # TODO change to None


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
        ret += f"POINTs 'pts' FILE 'out.loc'\n"
        ret += f"SPECout 'pts' SPEC2D ABS 'outputs/spec_out.nc' OUTPUT {self.spec.period.start.strftime(self._datefmt)} {out_intvl}\n"
        ret += f"TABle 'pts' HEADer 'outputs/tab_out.nc' TIME XP YP HS TPS TM01 DIR DSPR WIND OUTPUT {self.grid.period.start.strftime(self._datefmt)} {out_intvl}\n"
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
    spectral_resolution: SwanSpectrum = SwanSpectrum()
    forcing: ForcingData = ForcingData()
    physics: SwanPhysics = SwanPhysics()
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
        ret["remaining"] = f"BOUND NEST '{self.spectra_file}' CLOSED\n"
        ret["outputs"] = self.outputs.cmd
        ret["output_locs"] = self.outputs.spec.locations
        return ret


class SwanConfigPydantic(BaseConfig):
    """SWAN config class.

    Parameters
    ----------
    cgrid : CGRID
        The computational grid SWAN component.
    inpgrid: INPGRID
        The input grid SWAN component.

    """
    cgrid: COMPONENTS.get("cgrid")
    inpgrid: COMPONENTS.get("inpgrid")

    # def __repr__(self):
    #     s = ""
    #     for component in COMPONENTS:
    #         obj = getattr(self, component)
    #         if obj is not None:
    #             s += obj.render()
    #     return s

    def __str__(self):
        return self.__repr__()

    def _write_cmd(self):
        """Write command file."""
        repr = ""
        for component in COMPONENTS:
            obj = getattr(self, component)
            if obj is not None:
                # This works but is ugly
                if isinstance(obj, list):
                    for o in obj:
                        repr += o.render()
                else:
                    repr += obj.render()
        logger.info(f"Writing cmd file:\n{repr.strip()}")
        # with open(self.cmdfile, "w") as stream:
        #     logger.info(f"Writing cmd file:\n{repr.strip()}")
        #     stream.write(repr.strip())
        return repr