"""SWAN wave generation components.

This module contains components for configuring wave generation in SWAN.
"""

from typing import Literal, Optional, Union

from pydantic import Field

from rompy_swan.components.base import BaseComponent
from rompy_swan.components.physics._source_terms import (
    JANSSEN,
    KOMEN,
    ST6,
    ST6C1,
    ST6C2,
    ST6C3,
    ST6C4,
    ST6C5,
    WESTHUYSEN,
)


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
    """First generation source terms GEN1.

    .. code-block:: text

        GEN1 [cf10] [cf20] [cf30] [cf40] [edmlpm] [cdrag] [umin] [cfpm]

    With this command the user indicates that SWAN should run in first-generation mode
    (see Scientific/Technical documentation).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import GEN1
        gen = GEN1()
        print(gen.render())
        kwargs = dict(
            cf10=188.0,
            cf20=0.59,
            cf30=0.12,
            cf40=250.0,
            edmlpm=0.0036,
            cdrag=0.0012,
            umin=1.0,
            cfpm=0.13
        )
        gen = GEN1(**kwargs)
        print(gen.render())

    """

    model_type: Literal["gen1", "GEN1"] = Field(
        default="gen1", description="Model type discriminator"
    )
    cf10: Optional[float] = Field(
        default=None,
        description="Controls the linear wave growth (SWAN default: 188.0)",
    )
    cf20: Optional[float] = Field(
        default=None,
        description="Controls the exponential wave growth (SWAN default: 0.59)",
    )
    cf30: Optional[float] = Field(
        default=None,
        description="Controls the exponential wave growth (SWAN default: 0.12)",
    )
    cf40: Optional[float] = Field(
        default=None,
        description=(
            "Controls the dissipation rate, i.e., the time decay scale "
            "(SWAN default: 250.0)"
        ),
    )
    edmlpm: Optional[float] = Field(
        default=None,
        description=(
            "Maximum non-dimensionless energy density of the wind sea part of the "
            "spectrum according to Pierson Moskowitz (SWAN default: 0.0036)"
        ),
    )
    cdrag: Optional[float] = Field(
        default=None, description="Drag coefficient (SWAN default: 0.0012)"
    )
    umin: Optional[float] = Field(
        default=None,
        description=(
            "Minimum wind velocity (relative to current; all wind speeds "
            "are taken at 10 m above sea level) (SWAN default: 1)"
        ),
    )
    cfpm: Optional[float] = Field(
        default=None,
        description=(
            "Coefficient which determines the Pierson Moskowitz frequency: "
            "`delta_PM = 2pi g / U_10` (SWAN default: 0.13)"
        ),
    )

    def cmd(self):
        """Command line string for this component."""
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

    .. code-block:: text

        GEN2 [cf10] [cf20] [cf30] [cf40] [cf50] [cf60] [edmlpm] [cdrag] [umin] [cfpm]

    With this command the user indicates that SWAN should run in second-generation mode
    (see Scientific/Technical documentation).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import GEN2
        gen = GEN2()
        print(gen.render())
        kwargs = dict(
            cf10=188.0,
            cf20=0.59,
            cf30=0.12,
            cf40=250.0,
            cf50=0.0023,
            cf60=-0.223,
            edmlpm=0.0036,
            cdrag=0.0012,
            umin=1.0,
            cfpm=0.13
        )
        gen = GEN2(**kwargs)
        print(gen.render())

    """

    model_type: Literal["gen2", "GEN2"] = Field(
        default="gen2", description="Model type discriminator"
    )
    cf50: Optional[float] = Field(
        default=None,
        description=(
            "Controls the spectral energy scale of the limit spectrum "
            "(SWAN default: 0.0023)"
        ),
    )
    cf60: Optional[float] = Field(
        default=None,
        description=(
            "Ccontrols the spectral energy scale of the limit spectrum "
            "(SWAN default: -0.223"
        ),
    )

    def cmd(self):
        """Command line string for this component."""
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

    .. code-block:: text

        GEN3 JANSSEN|KOMEN|->WESTHUYSEN|ST6 AGROW [a]

    With this command the user indicates that SWAN should run in third-generation mode
    for wind input, quadruplet interactions and whitecapping.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import GEN3
        gen = GEN3(
            source_terms=dict(
                model_type="westhuysen",
                wind_drag="wu",
                agrow=True,
            ),
        )
        print(gen.render())
        from rompy_swan.components.physics._source_terms import ST6C1
        gen = GEN3(source_terms=ST6C1())
        print(gen.render())

    """

    model_type: Literal["gen3", "GEN3"] = Field(
        default="gen3", description="Model type discriminator"
    )
    source_terms: SOURCE_TERMS = Field(
        default_factory=WESTHUYSEN,
        description="SWAN source terms to be used (SWAN default: WESTHUYSEN)",
        discriminator="model_type",
    )

    def cmd(self):
        """Command line string for this component."""
        repr = f"GEN3 {self.source_terms.render()}"
        return repr
