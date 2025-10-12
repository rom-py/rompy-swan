"""SWAN physics limiter component.

This module contains the LIMITER component for controlling physics computations in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class LIMITER(BaseComponent):
    """Physics limiter.

    .. code-block:: text

        LIMITER [ursell] [qb]

    With this command the user can de-activate permanently the quadruplets when
    the actual Ursell number exceeds `ursell`. Moreover, as soon as the actual
    fraction of breaking waves exceeds `qb` then the action limiter will not be
    used in case of decreasing action density.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import LIMITER
        limiter = LIMITER()
        print(limiter.render())
        limiter = LIMITER(ursell=10.0, qb=1.0)
        print(limiter.render())

    """

    model_type: Literal["limiter", "LIMITER"] = Field(
        default="limiter", description="Model type discriminator"
    )
    ursell: Optional[float] = Field(
        default=None,
        description=("The upper threshold for Ursell number (SWAN default: 10.0)"),
    )
    qb: Optional[float] = Field(
        default=None,
        description="The threshold for fraction of breaking waves (SWAN default: 1.0)",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "LIMITER"
        if self.ursell is not None:
            repr += f" ursell={self.ursell}"
        if self.qb is not None:
            repr += f" qb={self.qb}"
        return repr
