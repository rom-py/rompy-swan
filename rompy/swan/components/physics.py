"""Model physics components."""
import logging
from typing import Literal, Optional, Union
from abc import ABC
from pydantic import validator, root_validator, constr, confloat, conint, Field

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
    ROGERS,
    ARDHUIN,
    ZIEGER,
    WCAPKOMEN,
    WCAPAB,
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


class GEN1(BaseComponent):
    """Physics component GEN1.

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
    """Physics component GEN2.

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
    """Physics component GEN3.

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


class PHYSICS(BaseComponent):
    """Physics component."""

    model_type: Literal["physics"] = Field(
        default="physics", description="Model type discriminator"
    )
    gen: GEN1 | GEN2 | GEN3 = Field(
        default=GEN3(),
        description="Wave generation",
        discriminator="model_type",
    )
    sswell: ROGERS | ARDHUIN | ZIEGER | None = Field(
        default=None,
        description="Swell dissipation type",
        discriminator="model_type",
    )
    wcapping: WCAPKOMEN | WCAPAB | None = Field(
        default=None,
        description="Swell dissipation type",
        discriminator="model_type",
    )

    @root_validator
    def deactivate_physics(cls, values):
        return values

    def cmd(self):
        repr = [self.gen.render()]
        if self.sswell is not None:
            repr += [f"{self.sswell.render()}"]
        if self.sswell is not None and self.sswell.model_type == "zieger":
            repr += [self.sswell.negatinp.render()]
        if self.wcapping is not None:
            repr += [self.wcapping.render()]
        return repr
