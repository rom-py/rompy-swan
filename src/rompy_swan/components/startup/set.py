"""SWAN SET component."""

from typing import Literal, Optional

from pydantic import Field, field_validator

from rompy.logging import get_logger
from rompy_swan.components.base import BaseComponent

logger = get_logger(__name__)


class SET(BaseComponent):
    """SWAN setting commands.

    .. code-block:: text

        SET [level] [nor] [depmin] [maxmes] [maxerr] [grav] [rho] [cdcap] &
            [inrhog] [hsrerr] NAUTICAL|->CARTESIAN [pwtail] [froudmax] [icewind]

    With this optional command the user assigns values to various general parameters.

    Notes
    -----
    The error level `maxerr` is coded as follows:

    * 1: warnings
    * 2: errors (possibly automatically repaired or repairable by SWAN)
    * 3: severe errors

    Default values for `pwtail` depend on formulations of physics:

    * command GEN1: `pwtail = 5`
    * command GEN2: `pwtail = 5`
    * command GEN3 KOMEN: `pwtail = 4`
    * command GEN3 WESTH: `pwtail = 4`
    * command GEN3 JANSSEN: `pwtail = 5`

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.startup.set import SET
        set = SET(level=0.5, direction_convention="nautical")
        print(set.render())
        set = SET(
            level=-1.0,
            nor=90,
            depmin=0.01,
            maxerr=3,
            grav=9.81,
            rho=1025,
            cdcap=2.5e-3,
            inrhog=0,
            hsrerr=0.1,
            direction_convention="nautical",
        )
        print(set.render())

    """

    model_type: Literal["set", "SET"] = Field(
        default="set", description="Model type discriminator"
    )
    level: Optional[float] = Field(
        default=None,
        description=(
            "Increase in water level that is constant in space and time can be given "
            "with this option, `level` is the value of this increase (in m). For a "
            "variable water level reference is made to the commands "
            "INPGRID and READINP (SWAN default: 0)"
        ),
        examples=[0],
    )
    nor: Optional[float] = Field(
        default=None,
        description=(
            "Direction of North with respect to the x-axis (measured "
            "counterclockwise); default `nor = 90`, i.e. x-axis of the problem "
            "coordinate system points East. When spherical coordinates are used "
            "(see command COORD) the value of `nor` may not be modified"
        ),
        ge=-360.0,
        le=360.0,
    )
    depmin: Optional[float] = Field(
        default=None,
        description=(
            "Threshold depth (in m). In the computation any positive depth smaller "
            "than `depmin` is made equal to `depmin` (SWAN default: 0.05)"
        ),
        ge=0.0,
    )
    maxmes: Optional[int] = Field(
        default=None,
        description=(
            "Maximum number of error messages during the computation at which the "
            "computation is terminated. During the computational process messages are "
            "written to the print file (SWAN default: 200)"
        ),
        ge=0,
    )
    maxerr: Optional[Literal[1, 2, 3]] = Field(
        default=None,
        description=(
            "During pre-processing SWAN checks input data. Depending on the severity "
            "of the errors encountered during this pre-processing, SWAN does not "
            "start computations. The user can influence the error level above which "
            "SWAN will  not start computations (at the level indicated the "
            "computations will continue) (SWAN default: 1)"
        ),
    )
    grav: Optional[float] = Field(
        default=None,
        description="The gravitational acceleration (in m/s2) (SWAN default: 9.81)",
        ge=0.0,
    )
    rho: Optional[float] = Field(
        default=None,
        description="The water density (in kg/m3) (SWAN default: 1025)",
        ge=0.0,
    )
    cdcap: Optional[float] = Field(
        default=None,
        description=(
            "The maximum value for the wind drag coefficient. A value of 99999 means"
            "no cutting off the drag coefficient. A suggestion for this parameter is "
            "`cdcap = 2.5x 10-3` (SWAN default: 99999) "
        ),
        ge=0.0,
    )
    inrhog: Optional[Literal[0, 1]] = Field(
        default=None,
        description=(
            "To indicate whether the user requires output based on variance or based "
            "on true energy (see Section 2.5). `inrhog` = 0: output based on variance, "
            "`inrhog` = 1: output based on true energy (SWAN default: 0)"
        ),
    )
    hsrerr: Optional[float] = Field(
        default=None,
        description=(
            "The relative difference between the user imposed significant wave height "
            "and the significant wave height computed by SWAN (anywhere along the "
            "computational grid boundary) above which a warning will be given. This "
            "relative difference is the difference normalized with the user provided "
            "significant wave height. This warning will be given for each boundary "
            "grid point where the problem occurs (with its x- and y-index number of "
            "the computational grid). The cause of the difference is explained in "
            "Section 2.6.3. To suppress these warnings (in particular for "
            "nonstationary computations), set `hsrerr` at a very high value or use "
            "command OFF BNDCHK (SWAN default: 0.10) (ONLY MEANT FOR STRUCTURED GRIDS)"
        ),
        ge=0.0,
    )
    direction_convention: Literal["nautical", "cartesian"] = Field(
        description=(
            "Direction convention: `nautical` indicates that the Nautical convention "
            "for wind and wave direction (SWAN input and output) will be used, "
            "`cartesian` indicates that the Cartesian convention for wind and wave "
            "direction will be used. For definition, see Section 2.5 or Appendix A "
            "(SWAN default: `cartesian`)"
        ),
    )
    pwtail: Optional[int] = Field(
        default=None,
        description=(
            "Power of high frequency tail; defines the shape of the spectral tail "
            "above the highest prognostic frequency `fhigh` (see command CGRID). "
            "The energy density is assumed to be proportional to frequency to the "
            "power `pwtail`. If the user wishes to use another value, then this SET "
            "command should be located in the command file after GEN1, GEN2 or GEN3 "
            "command (these will override the SET command with respect to `pwtail`)"
        ),
        ge=0,
    )
    froudmax: Optional[float] = Field(
        default=None,
        description=(
            "Is the maximum Froude number (`U/√gd` with `U` the current and `d` the "
            "water depth). The currents taken from a circulation model may mismatch "
            "with given water depth `d` in the sense that the Froude number becomes "
            "larger than 1. For this, the current velocities will be maximized by "
            "Froude number times `sqrt(gh)` (SWAN default: 0.8)"
        ),
        ge=0.0,
    )
    icewind: Optional[Literal[0, 1]] = Field(
        default=None,
        description=(
            "Controls the scaling of wind input by open water fraction. Default value "
            "of zero corresponds to the case where wind input is scaled by the open "
            "water fraction. If `icewind = 1` then sea ice does not affect wind input "
            "directly. (Though there is still indirect effect via the sea ice sink "
            "term; see command SICE) (SWAN default: 0)"
        ),
    )

    @field_validator("pwtail")
    @classmethod
    def pwtail_after_gen(cls, v):
        if v is not None:
            logger.warning("pwtail only has effect if set after GEN command")
        return v

    def cmd(self) -> str:
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
