"""SWAN output component."""

from typing import Literal

from pydantic import Field, field_validator

from rompy_swan.components.output.locations import BaseLocation
from rompy_swan.subcomponents.readgrid import GRIDREGULAR


class FRAME(BaseLocation):
    """Output locations on a regular grid.

    .. code-block:: text

        FRAME 'sname' [xpfr] [ypfr] [alpfr] [xlenfr] [ylenfr] [mxfr] [myfr]

    With this optional command the user defines output on a rectangular, uniform grid
    in a regular frame.

    If the set of output locations is identical to a part of the computational grid,
    then the user can use the alternative command GROUP.

    Note
    ----
    Cannot be used in 1D-mode.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import FRAME
        loc = FRAME(
            sname="outgrid",
            grid=dict(xp=173, yp=-40, xlen=2, ylen=2, mx=19, my=19),
        )
        print(loc.render())

    """

    model_type: Literal["frame", "FRAME"] = Field(
        default="frame", description="Model type discriminator"
    )
    grid: GRIDREGULAR = Field(description="Frame grid definition")

    @field_validator("grid")
    @classmethod
    def grid_suffix(cls, grid: GRIDREGULAR) -> GRIDREGULAR:
        grid.suffix = "fr"
        return grid

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"{super().cmd()} {self.grid.render()}"
        return repr
