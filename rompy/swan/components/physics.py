"""Model physics components."""
import logging
from typing import Literal, Optional, Union
from pydantic import validator, root_validator, Field, confloat

from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.physics import (
    JANSSEN,
    KOMEN,
    WESTHUYSEN,
    ST6,
    ST6C1,
    ST6C2,
    ST6C3,
    ST6C4,
    ST6C5,
    WCAPKOMEN,
    WCAPAB,
    QUADRUPL,
    CONSTANT,
    BKD,
    JONSWAP,
    COLLINS,
    MADSEN,
    RIPPLES,
)


logger = logging.getLogger(__name__)


SOURCE_TERMS = Union[
    JANSSEN,
    KOMEN,
    WESTHUYSEN,
    ST6,
    ST6C1,
    ST6C2,
    ST6C3,
    ST6C4,
    ST6C5,
]


#======================================================================================
# Wave generation GEN1 | GEN2 | GEN3
#======================================================================================
class GEN1(BaseComponent):
    """First generation source terms GEN1.

    `GEN1 [cf10] [cf20] [cf30] [cf40] [edmlpm] [cdrag] [umin] [cfpm]`

    With this command the user indicates that SWAN should run in first-generation mode
    (see Scientific/Technical documentation).

    """

    model_type: Literal["gen1"] = Field(
        default="gen1", description="Model type discriminator"
    )
    cf10: Optional[float] = Field(
        description="Controls the linear wave growth (SWAN default: 188.0)"
    )
    cf20: Optional[float] = Field(
        description="Controls the exponential wave growth (SWAN default: 0.59)"
    )
    cf30: Optional[float] = Field(
        description="Controls the exponential wave growth (SWAN default: 0.12)"
    )
    cf40: Optional[float] = Field(
        description="Controls the dissipation rate, i.e., the time decay scale (SWAN default: 250.0)"
    )
    edmlpm: Optional[float] = Field(
        description="Maximum non-dimensionless energy density of the wind sea part of the spectrum according to Pierson Moskowitz (SWAN default: 0.0036)"
    )
    cdrag: Optional[float] = Field(
        description="Drag coefficient (SWAN default: 0.0012)"
    )
    umin: Optional[float] = Field(
        description="Minimum wind velocity (relative to current; all wind speeds are taken at 10 m above sea level) (SWAN default: 1)"
    )
    cfpm: Optional[float] = Field(
        description="Coefficient which determines the Pierson Moskowitz frequency: $delta_{PM} = 2pi g / U_{10}$ (SWAN default: 0.13)"
    )

    def cmd(self):
        repr = "GEN1"
        if self.cf10 is not None:
            repr += f" cf10={self.cf10}"
        if self.cf20 is not None:
            repr += f" cf20={self.cf20}"
        if self.cf30 is not None:
            repr += f" cf30={self.cf30}"
        if self.cf40 is not None:
            repr += f" cf40={self.cf40}"
        if self.edmlpm is not None:
            repr += f" edmlpm={self.edmlpm}"
        if self.cdrag is not None:
            repr += f" cdrag={self.cdrag}"
        if self.umin is not None:
            repr += f" umin={self.umin}"
        if self.cfpm is not None:
            repr += f" cfpm={self.cfpm}"
        return repr


class GEN2(GEN1):
    """Second generation source terms GEN2.

    `GEN2 [cf10] [cf20] [cf30] [cf40] [cf50] [cf60] [edmlpm] [cdrag] [umin] [cfpm]`

    With this command the user indicates that SWAN should run in second-generation mode
    (see Scientific/Technical documentation).

    """

    model_type: Literal["gen2"] = Field(
        default="gen2", description="Model type discriminator"
    )
    cf50: Optional[float] = Field(
        description="Controls the spectral energy scale of the limit spectrum (SWAN default: 0.0023)"
    )
    cf60: Optional[float] = Field(
        description="Ccontrols the spectral energy scale of the limit spectrum (SWAN default: -0.223"
    )

    def cmd(self):
        repr = "GEN2"
        if self.cf10 is not None:
            repr += f" cf10={self.cf10}"
        if self.cf20 is not None:
            repr += f" cf20={self.cf20}"
        if self.cf30 is not None:
            repr += f" cf30={self.cf30}"
        if self.cf40 is not None:
            repr += f" cf40={self.cf40}"
        if self.cf50 is not None:
            repr += f" cf50={self.cf50}"
        if self.cf60 is not None:
            repr += f" cf60={self.cf60}"
        if self.edmlpm is not None:
            repr += f" edmlpm={self.edmlpm}"
        if self.cdrag is not None:
            repr += f" cdrag={self.cdrag}"
        if self.umin is not None:
            repr += f" umin={self.umin}"
        if self.cfpm is not None:
            repr += f" cfpm={self.cfpm}"
        return repr


class GEN3(BaseComponent):
    """Third generation source terms GEN3.

    `GEN3 JANSSEN|KOMEN|WESTHUYSEN|ST6 (...) AGROW [a]`

    With this command the user indicates that SWAN should run in third-generation mode
    for wind input, quadruplet interactions and whitecapping.

    """

    model_type: Literal["gen3"] = Field(
        default="gen3", description="Model type discriminator"
    )
    source_terms: SOURCE_TERMS = Field(
        default=WESTHUYSEN(), description="SWAN source terms to be used"
    )

    @root_validator
    def check_source_terms(cls, values):
        return values

    def cmd(self):
        repr = f"GEN3 {self.source_terms.render()}"
        return repr


#======================================================================================
# Swell dissipation SSWELL
#======================================================================================
class NEGATINP(BaseComponent):
    """Negative wind input.

    With this optional command the user activates negative wind input. **This is intended
    only for use with non-breaking swell dissipation SSWELL ZIEGER**. Parameter `rdcoef`
    is a fraction between 0 and 1, representing the strength of negative wind input. As
    an example, with [rdcoef]=0.04, for a spectral bin that is opposed to the wind
    direction, the wind input factor W(k, θ) is negative, and its magnitude is 4% of
    the corresponding value of the spectral bin that is in the opposite direction
    (i.e. in the wind direction). See Zieger et al. (2015) eq. 11, where a0 is their
    notation for [rdcoef]. Default [rdcoef]=0.0 and `rdcoef=0.04` is recommended,
    though as implied by Zieger et al. (2015), this value is not well-established, so
    the user is encouraged to experiment with other values.

    References
    ----------
    Zieger, S., A.V. Babanin, W. E. Rogers and I.R. Young, 2015: Observation-based
    source terms in the third-generation wave model WAVEWATCH, Ocean Model., 96, 2-25.

    """

    model_type: Literal["negatinp"] = Field(
        default="negatinp", description="Model type discriminator"
    )
    rdcoef: confloat(ge=0.0, le=1.0) = Field(
        default=0.0,
        description="Coefficient representing the strength of negative wind input",
    )

    def cmd(self) -> str:
        return f"NEGATINP rdcoef={self.rdcoef}"


class SSWELL(BaseComponent):
    """Swell dissipation sub-component.

    `SSWELL base component.`

    With this command the user can influence the type of swell dissipation included in
    the computations. The Zieger option is intended for use with negative wind input
    via the NEGATINP command. Zieger non-breaking dissipation follows the method used
    in WAVEWATCH III version 4 and does not include the steepness-dependent swell
    coefficient introduced in WAVEWATCH III version 5. As noted already, if
    `GEN3 ST6...` command is used, this SSWELL command should be provided.

    """

    model_type: Literal["sswell"] = Field(
        default="sswell", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return "SSWELL"


class ROGERS(SSWELL):
    """Nonbreaking dissipation of Rogers et al. (2012).

    References
    ----------
    Rogers, W.E., A.V. Babanin and D.W. Wang, 2012: Observation-Consistent Input and
    Whitecapping Dissipation in a Model for Wind-Generated Surface Waves: Description
    and Simple Calculations, J. Atmos. Oceanic Technol., 29:9, 1329-1346.

    """

    model_type: Literal["rogers"] = Field(
        default="rogers", description="Model type discriminator"
    )
    cdsv: Optional[float] = Field(
        description="Coefficient related to laminar atmospheric boundary layer (SWAN default: 1.2)"
    )
    feswell: Optional[float] = Field(
        description="Swell dissipation factor"
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} ROGERS"
        if self.cdsv is not None:
            repr += f" cdsv={self.cdsv}"
        if self.feswell is not None:
            repr += f" feswell={self.feswell}"
        return repr


class ARDHUIN(SSWELL):
    """Nonbreaking dissipation of Ardhuin et al. (2010).

    References
    ----------
    Ardhuin, F., A. Rogers, A. Babanin, J. Filipot, J. Magne, A. Roland, and P. van
    der Westhuysen, 2010: Semiempirical dissipation source functions for ocean waves.
    Part I: Definition, calibration, and validation, J. Phys. Oceanogr., 40, 1917-1941.

    """

    model_type: Literal["ardhuin"] = Field(
        default="ardhuin", description="Model type discriminator"
    )
    cdsv: Optional[float] = Field(
        description="Coefficient related to laminar atmospheric boundary layer (SWAN default: 1.2)"
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} ARDHUIN"
        if self.cdsv is not None:
            repr += f" cdsv={self.cdsv}"
        return repr


class ZIEGER(SSWELL):
    """Nonbreaking dissipation of Zieger et al. (2015).

    Swell dissipation of Young et al. (2013) updated by Zieger et al. (2015).

    References
    ----------
    Zieger, S., A.V. Babanin, W. E. Rogers and I.R. Young, 2015: Observation-based
    source terms in the third-generation wave model WAVEWATCH, Ocean Model., 96, 2-25.

    Young, I.R., A.V.Babanin and S. Zieger, 2013: The Decay Rate of Ocean Swell
    Observed by Altimeter, J. Phys. Oceanogr., 43, 3233-3233.

    """

    model_type: Literal["zieger"] = Field(
        default="zieger", description="Model type discriminator"
    )
    b1: Optional[float] = Field(
        description="Non-dimensional proportionality coefficient"
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} ZIEGER"
        if self.b1 is not None:
            repr += f" b1={self.b1}"
        return repr


#======================================================================================
# Physics group component
#======================================================================================
class PHYSICS(BaseComponent):
    """Physics component."""

    model_type: Literal["physics"] = Field(
        default="physics", description="Model type discriminator"
    )
    gen: GEN1 | GEN2 | GEN3 = Field(
        default=GEN3(),
        description="Wave generation specification",
        discriminator="model_type",
    )
    sswell: ROGERS | ARDHUIN | ZIEGER | None = Field(
        default=None,
        description="Swell dissipation specification",
        discriminator="model_type",
    )
    negatinp: Optional[NEGATINP] = Field(
        default=None,
        description="Negative wind input specification",
    )
    wcapping: WCAPKOMEN | WCAPAB | None = Field(
        default=None,
        description="Whitecapping specification",
        discriminator="model_type",
    )
    quadrupl: Optional[QUADRUPL] = Field(
        description="Quadruplet interactions specification",
    )
    breaking: CONSTANT | BKD | None = Field(
        description="Wave breaking specification",
        discriminator="model_type",
    )
    friction: JONSWAP | COLLINS | MADSEN | RIPPLES | None = Field(
        default=JONSWAP(),
        description="Bottom friction specification",
    )

    @root_validator
    def deactivate_physics(cls, values):
        return values

    @validator("negatinp", pre=False)
    def negatinp_only_with_zieger(cls, value, values):
        """Log a warning if NEGATINP is used with a non-ZIEGER SSWELL."""
        if values["sswell"] is None:
            logger.warning(
                "The negative wind input NEGATINP is only intended to use with the "
                "swell dissipation SSWELL ZIEGER but no SSWELL has been specified."
            )
        elif values["sswell"].model_type != "zieger":
            logger.warning(
                "The negative wind input NEGATINP is only intended to use with the "
                "swell dissipation SSWELL ZIEGER but "
                f"SSWELL {values['sswell'].model_type.upper()} has been specified."
            )
        return value

    def cmd(self):
        repr = [self.gen.render()]
        if self.sswell is not None:
            repr += [f"{self.sswell.render()}"]
        if self.negatinp is not None:
            repr += [self.negatinp.render()]
        if self.wcapping is not None:
            repr += [self.wcapping.render()]
        if self.quadrupl is not None:
            repr += [self.quadrupl.render()]
        if self.breaking is not None:
            repr += [self.breaking.render()]
        if self.friction is not None:
            repr += [self.friction.render()]
        return repr
