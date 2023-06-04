"""Model start up components."""
import logging
from typing import Literal, Optional
from pydantic import validator, root_validator, constr, confloat, conint

from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.startup import CARTESIAN, SPHERICAL

logger = logging.getLogger(__name__)


class PROJECT(BaseComponent):
    """SWAN Project component.

    `PROJECT 'name' 'nr' 'title' 'title2 'title3'`

    Parameters
    ----------
    model_type: Literal["project"]
        Model type discriminator.
    name: Optional[str]
        Is the name of the project, at most 16 characters long.
    nr: str
        Is the run identification (to be provided as a character string; e.g. the run
        number) to distinguish this run among other runs for the same project; it is at
        most 4 characters long. It is the only required information in this command.
    title1: Optional[str]
        Is a string of at most 72 characters provided by the user to appear in the
        output of the program for the user's convenience. Default: blanks.
    title2: Optional[str]
        Same as 'title1'.
    title3: Optional[str]
        Same as 'title1'.

    With this required command the user defines a number of strings to identify the
    SWAN run (project name e.g., an engineering project) in the print and plot file.

    """
    model_type: Literal["project"] = "project"
    name: Optional[constr(max_length=16)]
    nr: constr(max_length=4)
    title1: Optional[constr(max_length=72)]
    title2: Optional[constr(max_length=72)]
    title3: Optional[constr(max_length=72)]

    def __repr__(self):
        repr = "PROJECT"
        if self.name is not None:
            repr += f" name='{self.name}'"
        repr += f" nr='{self.nr}'"
        if self.title1 is not None:
            repr += f" title1='{self.title1}'"
        if self.title2 is not None:
            repr += f" title2='{self.title2}'"
        if self.title3 is not None:
            repr += f" title3='{self.title3}'"
        return repr


class SET(BaseComponent):
    """SWAN SET component.

    `SET [level] [nor] [depmin] [maxmes] [maxerr] [grav] [rho] [cdcap] &`
        `[inrhog] [hsrerr] NAUTICAL|CARTESIAN [pwtail] [froudmax] [icewind]`

    Parameters
    ----------
    model_type: Literal["set"]
        Model type discriminator.
    level: float
        Increase in water level that is constant in space and time can be given with
        this option, `level` is the value of this increase (in m). For a variable water
        level reference is made to the commands INPGRID and READINP. Default: `level = 0`.
    nor: str
        Direction of North with respect to the x-axis (measured counterclockwise);
        default `nor = 90`, i.e. x-axis of the problem coordinate system points East.
        When spherical coordinates are used (see command COORD) the value of `nor` may
        not be modified.
    depmin: float
        Threshold depth (in m). In the computation any positive depth smaller than
        `depmin` is made equal to `depmin`. Default: `depmin = 0.05`.
    maxmes: int
        Maximum number of error messages during the computation at which the
        computation is terminated. During the computational process messages are
        written to the print file. Default: `maxmes = 200`.
    maxerr: int
        During pre-processing SWAN checks input data. Depending on the severity
        of the errors encountered during this pre-processing, SWAN does not start
        computations. The user can influence the error level above which SWAN will
        not start computations (at the level indicated the computations will continue).
        The error level `maxerr` is coded as follows:
            1: warnings.
            2: errors (possibly automatically repaired or repairable by SWAN).
            3: severe errors.
        Default: `maxerr = 1`.
    grav: float
        The gravitational acceleration (in m/s2). Default: `grav = 9.81`.
    rho: float
        The water density (in kg/m3). Default: `rho = 1025`.
    cdcap: float
        The maximum value for the wind drag coefficient. A value of `cdcap = 99999`
        means no cutting off the drag coefficient. A suggestion for this parameter is
        `cdcap = 2.5x 10-3`. Default: `cdcap = 99999`.
    inrhog: int
        To indicate whether the user requires output based on variance or based on true
        energy (see Section 2.5).
            `inrhog` = 0: output based on variance.
            `inrhog` = 1: output based on true energy.
        Default: `inrhog=0`.
    hsrerr: float
        The relative difference between the user imposed significant wave height and
        the significant wave height computed by SWAN (anywhere along the computational
        grid boundary) above which a warning will be given. This relative difference is
        the difference normalized with the user provided significant wave height. This
        warning will be given for each boundary grid point where the problem occurs
        (with its x- and y-index number of the computational grid). The cause of the
        difference is explained in Section 2.6.3. To suppress these warnings (in
        particular for nonstationary computations), set `hsrerr` at a very high value
        or use command OFF BNDCHK. Default: `hsrerr = 0.10`.
        ONLY MEANT FOR STRUCTURED GRIDS.
    direction_convention: Literal["nautical", "cartesian"]
        - NAUTICAL: Indicates that the Nautical convention for wind and wave direction
          (SWAN input and output) will be used instead of the default Cartesian
          convention. For definition, see Section 2.5 or Appendix A.
        - CARTESIAN: Indicates that the Cartesian convention for wind and wave
          direction (SWAN input and output) will be used. For definition,
          see Section 2.5 or Appendix A.
    pwtail: int
        Power of high frequency tail; defines the shape of the spectral tail above the
        highest prognostic frequency `fhigh` (see command CGRID). The energy density
        is assumed to be proportional to frequency to the power `pwtail`.
        Default values depend on formulations of physics:
            - command GEN1: `pwtail = 5`.
            - command GEN2: `pwtail = 5`.
            - command GEN3 KOMEN: `pwtail = 4`.
            - command GEN3 WESTH: pwtail = 4`.
            - command GEN3 JANSSEN: `pwtail = 5`.
        If the user wishes to use another value, then this SET command should be
        located in the command file after the GEN1, GEN2 or GEN3 command (these will
        override the SET command with respect to `pwtail`).    
    froudmax: float
        Is the maximum Froude number (`U/√gd` with `U` the current and `d` the water
        depth). The currents taken from a circulation model may mismatch with given
        water depth `d` in the sense that the Froude number becomes larger than 1.
        For this, the current velocities will be maximized by Froude number times
        `√gd`. Default: `froudmax = 0.8`.
    icewind: float
        Controls the scaling of wind input by open water fraction. Default value of zero
        corresponds to the case where wind input is scaled by the open water fraction.
        If `icewind = 1` then sea ice does not affect wind input directly. (Though
        there is still indirect effect via the sea ice sink term; see command SICE.)
        Default: `icewind = 0`.

    With this optional command the user assigns values to various general parameters.

    """
    model_type: Literal["set"] = "set"
    level: Optional[confloat(ge=0.0)]
    nor: Optional[confloat(ge=-360.0, le=360.0)]
    depmin: Optional[confloat(ge=0.0)]
    maxmes: Optional[conint(ge=0)]
    maxerr: Literal[1, 2, 3, None] = None
    grav: Optional[confloat(ge=0.0)]
    rho: Optional[confloat(ge=0.0)]
    cdcap: Optional[confloat(ge=0.0)]
    inrhog: Literal[0, 1, None] = None
    hsrerr: Optional[confloat(ge=0.0)]
    direction_convention: Literal["nautical", "cartesian"]
    pwtail: Optional[conint(ge=0)]
    froudmax: Optional[confloat(ge=0.0)]
    icewind: Literal[0, 1, None] = None

    @validator("pwtail")
    def pwtail_after_gen(cls, v):
        if v is not None:
            logger.warning("pwtail only has effect if set after GEN command")
        return v

    def __repr__(self):
        repr = "SET"
        if self.level is not None:
            repr += f" level={self.level}"
        if self.nor is not None:
            repr += f" nor={self.nor}"
        if self.depmin is not None:
            repr += f" depmin={self.depmin}"
        if self.maxmes is not None:
            repr += f" maxmes={self.maxmes}"
        if self.maxerr is not None:
            repr += f" maxerr={self.maxerr}"
        if self.grav is not None:
            repr += f" grav={self.grav}"
        if self.rho is not None:
            repr += f" rho={self.rho}"
        if self.cdcap is not None:
            repr += f" cdcap={self.cdcap}"
        if self.inrhog is not None:
            repr += f" inrhog={self.inrhog}"
        if self.hsrerr is not None:
            repr += f" hsrerr={self.hsrerr}"
        if self.direction_convention is not None:
            repr += f" {self.direction_convention.upper()}"
        if self.pwtail is not None:
            repr += f" pwtail={self.pwtail}"
        if self.froudmax is not None:
            repr += f" froudmax={self.froudmax}"
        if self.icewind is not None:
            repr += f" icewind={self.icewind}"
        return repr


class MODE(BaseComponent):
    """SWAN Mode component.

    `MODE STATIONARY|NONSTATIONARY TWODIMENSIONAL|ONEDIMENSIONAL`

    Parameters
    ----------
    model_type: Literal["mode"]
        Model type discriminator.
    kind: Literal["stationary", "nonstationary"]
        Indicates that the run will be either stationary or nonstationary.
    dim: Literal["twodimensional", "onedimensional"]
        Indicates that the run will be either one-dimensional (1D-mode) or
        two-dimensional (2D-mode).

    With this optional command the user indicates that the run will be either stationary
    or nonstationary and one-dimensional (1D-mode) or two-dimensional (2D-mode). Non-
    stationary means either (see command COMPUTE):
    (a) one nonstationary computations or
    (b) a sequence of stationary computations or
    (c) a mix of (a) and (b).

    """
    model_type: Literal["mode"] = "mode"
    kind: Literal["stationary", "nonstationary"] = "stationary"
    dim: Literal["onedimensional", "twodimensional"] = "twodimensional"

    def __repr__(self):
        return f"MODE {self.kind.upper()} {self.dim.upper()}"



class COORDINATES(BaseComponent):
    """SWAN Coordinates component.

    `COORDINATES CARTESIAN|SPHERICAL REPEATING`

    Parameters
    ----------
    model_type: Literal["coordinates"]
        Model type discriminator.
    kind: CARTESIAN | SPHERICAL
        Coordinates kind.
    repeating: bool
        This option is only for academic cases. It means that wave energy leaving at
        one end of the domain (in computational x-direction) enter at the other side;
        it is as if the wave field repeats itself in x-direction with the length of the
        domain in x-direction. This option cannot be used in combination with
        computation of set-up (see command SETUP). This option is available only with
        regular grids.

    Command to choose between Cartesian and spherical coordinates (see Section 2.5).
    A nested SWAN run must use the same coordinate system as the coarse grid SWAN run.

    """
    model_type: Literal["coordinates"] = "coordinates"
    kind: CARTESIAN | SPHERICAL = CARTESIAN()
    reapeating: bool = False

    def __repr__(self):
        repr = f"COORDINATES {self.kind.render()}"
        if self.reapeating:
            repr += " REPEATING"
        return repr
