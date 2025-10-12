"""SWAN wave breaking components.

This module contains components for configuring wave breaking in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class BREAKING_CONSTANT(BaseComponent):
    """Constant wave breaking index.

    .. code-block:: text

        BREAKING CONSTANT [alpha] [gamma]

    Indicates that a constant breaker index is to be used.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import BREAKING_CONSTANT
        breaking = BREAKING_CONSTANT()
        print(breaking.render())
        breaking = BREAKING_CONSTANT(alpha=1.0, gamma=0.73)
        print(breaking.render())

    """

    model_type: Literal["constant", "CONSTANT"] = Field(
        default="constant", description="Model type discriminator"
    )
    alpha: Optional[float] = Field(
        default=None,
        description=(
            "Proportionality coefficient of the rate of dissipation "
            "(SWAN default: 1.0)"
        ),
    )
    gamma: Optional[float] = Field(
        default=None,
        description=(
            "The breaker index, i.e. the ratio of maximum individual wave height "
            "over depth (SWAN default: 0.73)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "BREAKING CONSTANT"
        if self.alpha is not None:
            repr += f" alpha={self.alpha}"
        if self.gamma is not None:
            repr += f" gamma={self.gamma}"
        return repr


class BREAKING_BKD(BaseComponent):
    """Variable wave breaking index.

    .. code-block:: text

        BREAKING BKD [alpha] [gamma0] [a1] [a2] [a3]

    Indicates that the breaker index scales with both the bottom slope (`beta`)
    and the dimensionless depth (kd).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import BREAKING_BKD
        breaking = BREAKING_BKD()
        print(breaking.render())
        breaking = BREAKING_BKD(alpha=1.0, gamma0=0.54, a1=7.59, a2=-8.06, a3=8.09)
        print(breaking.render())

    """

    model_type: Literal["bkd", "BKD"] = Field(
        default="bkd", description="Model type discriminator"
    )
    alpha: Optional[float] = Field(
        default=None,
        description=(
            "Proportionality coefficient of the rate of dissipation "
            "(SWAN default: 1.0)"
        ),
    )
    gamma0: Optional[float] = Field(
        default=None,
        description="The reference $gamma$ for horizontal slopes (SWAN default: 0.54)",
    )
    a1: Optional[float] = Field(
        default=None,
        description=(
            "First tunable coefficient for the breaker index (SWAN default: 7.59)"
        ),
    )
    a2: Optional[float] = Field(
        default=None,
        description=(
            "Second tunable coefficient for the breaker index (SWAN default: -8.06)"
        ),
    )
    a3: Optional[float] = Field(
        default=None,
        description=(
            "Third tunable coefficient for the breaker index (SWAN default: 8.09)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "BREAKING BKD"
        if self.alpha is not None:
            repr += f" alpha={self.alpha}"
        if self.gamma0 is not None:
            repr += f" gamma0={self.gamma0}"
        if self.a1 is not None:
            repr += f" a1={self.a1}"
        if self.a2 is not None:
            repr += f" a2={self.a2}"
        if self.a3 is not None:
            repr += f" a3={self.a3}"
        return repr
