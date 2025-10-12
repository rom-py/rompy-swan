"""SWAN turbulence component.

This module contains the TURBULENCE component for turbulent viscosity in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field, model_validator

from rompy_swan.components.base import BaseComponent


class TURBULENCE(BaseComponent):
    """Turbulent viscosity.

    .. code-block:: text

        TURBULENCE [ctb] (CURRENT [tbcur])

    With this optional command the user can activate turbulent viscosity. This physical
    effect is also activated by reading values of the turbulent viscosity using the
    `READGRID TURB` command, but then with the default value of `ctb`. The command
    `READGRID TURB` is necessary if this command `TURB` is used since the value of the
    viscosity is assumed to vary over space.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import TURBULENCE
        turbulence = TURBULENCE(current=False)
        print(turbulence.render())
        turbulence = TURBULENCE(ctb=0.01, current=True, tbcur=0.004)
        print(turbulence.render())

    """

    model_type: Literal["turbulence", "TURBULENCE"] = Field(
        default="turbulence", description="Model type discriminator"
    )
    ctb: Optional[float] = Field(
        default=None,
        description=(
            "The value of the proportionality coefficient appearing in the energy "
            "dissipation term (SWAN default: 0.01)"
        ),
    )
    current: Optional[bool] = Field(
        default=True,
        description=(
            "If this keyword is present the turbulent viscosity will be derived from "
            "the product of the depth and the absolute value of the current velocity. "
            "If the command `READGRID TURB` is used, this option is ignored; "
            "the values read from file will prevail"
        ),
    )
    tbcur: Optional[float] = Field(
        default=None,
        description=(
            "The factor by which depth x current velocity is multiplied in order to "
            "get the turbulent viscosity (SWAN default: 0.004)"
        ),
    )

    @model_validator(mode="after")
    def tbcur_only_with_current(self) -> "TURBULENCE":
        if not self.current and self.tbcur is not None:
            raise ValueError("`tbcur` can only be defined if `current` is True")
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "TURBULENCE"
        if self.ctb is not None:
            repr += f" ctb={self.ctb}"
        if self.current:
            repr += " CURRENT"
        if self.tbcur is not None:
            repr += f" tbcur={self.tbcur}"
        return repr
