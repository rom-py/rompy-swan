import os
import logging
import platform
from datetime import datetime

from pydantic import validator

from rompy import TEMPLATES_DIR
from rompy.core import BaseConfig, Coordinate, DateTimeRange, RompyBaseModel
from rompy.swan.components import cgrid, inpgrid

from .grid import SwanGrid


logger = logging.getLogger(__name__)


# All supported swan components must be specified here
COMPONENTS = {
    "cgrid": cgrid.REGULAR | cgrid.CURVILINEAR | cgrid.UNSTRUCTURED,
    "inpgrid": list[inpgrid.REGULAR | inpgrid.CURVILINEAR | inpgrid.UNSTRUCTURED],
}


class SwanConfigPydantic(RompyBaseModel):
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

    def __repr__(self):
        s = ""
        for component in COMPONENTS:
            obj = getattr(self, component)
            if obj is not None:
                s += obj.render()
        return s

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


class OutputLocs(RompyBaseModel):
    """Output locations for SWAN
q
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
    out_start: datetime | None = None
    out_intvl: str = "1.0 HR"
    output_locs: OutputLocs = OutputLocs()
    #    wind_source: SwanDataGrid = SwanDataGrid()
    wind_grid: str = "REG 115.3 -32.8 0.0 2 3 0.3515625 0.234375  NONSTATION 20200221.040000  10800.0 S"
    wind_read: str = "SERIES 'extracted.wind' 1 FORMAT '(3F8.1)'"
    bottom_grid: str = "REG 115.68 -32.76 77 390 150 0.001 0.001 EXC -99.0"
    bottom_file: str = "bathy.bot"
    friction: str = "MAD"
    friction_coeff: str = "0.1"
    spectra_file: str = "boundary.spec"
    # subnests: list[SwanConfig] = []

    @validator("out_start", "out_intvl", pre=True)
    def validate_out_start_intvl(cls, v):
        return cls.validate_compute_start_stop(v)

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
        self._generated_at = str(datetime.utcnow())
        self._generated_by = os.environ.get("USER")
        self._generated_on = platform.node()

        if not self.out_start:
            self.out_start = runtime.compute_start
        if not self.out_intvl:
            self.out_intvl = (
                "1.0 HR"  # Hardcoded for now, need to get from time object too
            )
        frequency = "0.25 HR"  # Hardcoded for now, need to get from time object too
        output = ""
        output += f"$\n"
        output += f"$ SWAN - Simple example template used by rompy\n"
        output += f"$ Template: \n"
        output += f"$ Generated: {self._generated_at} on {self._generated_on} by {self._generated_by}\n"
        output += f"$ projection: wgs84\n"
        output += f"$\n"
        output += "\n"
        output += f"MODE NONSTATIONARY TWODIMENSIONAL\n"
        output += f"COORDINATES SPHERICAL\n"
        output += f"SET NAUTICAL\n"
        output += "\n"
        output += f"CGRID {self.cgrid.cgrid} CIRCLE 36 0.0464 1. 31\n"
        output += f"{self.cgrid.cgrid_read}\n"
        output += "\n"
        output += f"INPGRID BOTTOM {self.bottom_grid}\n"
        output += f"READINP BOTTOM 1 '{self.bottom_file}' 3 0 FREE\n"
        output += "\n"
        output += f"INPGRID WIND {self.wind_grid}\n"
        output += f"READINP WIND {self.wind_read}\n"
        output += "\n"
        output += f"GEN3 WESTH 0.000075 0.00175\n"
        output += f"BREAKING\n"
        output += f"FRICTION {self.friction} {self.friction_coeff}\n"
        output += "\n"
        output += f"TRIADS\n"
        output += "\n"
        output += f"PROP BSBT\n"
        output += f"NUM ACCUR 0.02 0.02 0.02 95 NONSTAT 20\n"
        output += "\n"
        output += f"BOUND NEST '{self.spectra_file}' CLOSED\n"
        output += "\n"
        output += f"OUTPUT OPTIONS BLOCK 8\n"
        output += f"BLOCK 'COMPGRID' HEADER 'outputs/swan_out.nc' LAYOUT 1 DEPTH UBOT HSIGN HSWELL DIR TPS TM01 WIND OUT {self.out_start.strftime(self._datefmt)} {self.out_intvl}\n"
        output += "\n"
        output += f"POINTs 'pts' FILE 'out.loc'\n"
        output += f"SPECout 'pts' SPEC2D ABS 'outputs/spec_out.nc' OUTPUT {self.out_start.strftime(self._datefmt)} {self.out_intvl}\n"
        output += f"TABle 'pts' HEADer 'outputs/tab_out.nc' TIME XP YP HS TPS TM01 DIR DSPR WIND OUTPUT {self.out_start.strftime(self._datefmt)} {self.out_intvl}\n"
        output += "\n"
        output += f"COMPUTE NONST {runtime.compute_start.strftime(self._datefmt)} {frequency} {runtime.compute_stop.strftime(self._datefmt)}\n"
        output += "\n"
        output += f"STOP\n"
        return output

    def write(self, runtime) -> None:
        """Write SWAN input file

        Parameters
        ----------
        run_dir : str
            Path to run directory
        """
        outdir = os.path.join(runtime.output_dir, runtime.run_id)
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "INPUT"), "w") as f:
            f.write(self.generate(runtime=runtime))
