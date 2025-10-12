"""SWAN MODE component."""

from typing import Literal

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class MODE(BaseComponent):
    """SWAN Mode.

    .. code-block:: text

        MODE ->STATIONARY|NONSTATIONARY ->TWODIMENSIONAL|ONEDIMENSIONAL

    With this optional command the user indicates that the run will be either
    stationary or nonstationary and one-dimensional (1D-mode) or two-dimensional
    (2D-mode). Nonstationary means either (see command COMPUTE):

    * (a) one nonstationary computations or
    * (b) a sequence of stationary computations or
    * (c) a mix of (a) and (b)

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.startup.mode import MODE
        mode = MODE()
        print(mode.render())
        mode = MODE(kind="nonstationary", dim="twodimensional")
        print(mode.render())

    """

    model_type: Literal["mode", "MODE"] = Field(
        default="mode", description="Model type discriminator."
    )
    kind: Literal["stationary", "nonstationary"] = Field(
        default="stationary",
        description="Indicates if run will be stationary or nonstationary",
    )
    dim: Literal["onedimensional", "twodimensional"] = Field(
        default="twodimensional",
        description=(
            "Indicates that the run will be either one-dimensional (1D-mode) or "
            "two-dimensional (2D-mode)"
        ),
    )

    def cmd(self) -> str:
        return f"MODE {self.kind.upper()} {self.dim.upper()}"
