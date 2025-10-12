"""SWAN output component."""

from abc import ABC
from typing import Annotated, Literal, Optional, Union

from pydantic import Field, field_validator, model_validator

from rompy.logging import get_logger
from rompy_swan.components.base import BaseComponent, MultiComponents
from rompy_swan.subcomponents.base import IJ, XY
from rompy_swan.subcomponents.output import ABS, REL, SPEC1D, SPEC2D
from rompy_swan.subcomponents.readgrid import GRIDREGULAR
from rompy_swan.subcomponents.time import TimeRangeOpen
from rompy_swan.types import IDLA, BlockOptions

logger = get_logger(__name__)

SPECIAL_NAMES = ["BOTTGRID", "COMPGRID", "BOUNDARY", "BOUND_"]


class BaseLocation(BaseComponent, ABC):
    """Base class for SWAN output locations.

    .. code-block:: text

        {MODEL_TYPE} sname='sname'

    This is the base class for all locations components. It is not meant to be used
    directly.

    Note
    ----
    The name of the set of output locations `sname` cannot be longer than 8 characters
    and must not match any SWAN special names such as `BOTTGRID` (define output over
    the bottom/current grid) or `COMPGRID` (define output over the computational grid).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import BaseLocation
        loc = BaseLocation(sname="outsites")
        print(loc.render())

    """

    model_type: Literal["locations", "LOCATIONS"] = Field(
        default="locations",
        description="Model type discriminator",
    )
    sname: str = Field(
        description="Name of the set of output locations defined by this command",
        max_length=8,
    )

    @field_validator("sname")
    @classmethod
    def not_special_name(cls, sname: str) -> str:
        """Ensure sname is not defined as one of the special names."""
        for name in SPECIAL_NAMES:
            if sname.upper().startswith(name):
                raise ValueError(f"sname {sname} is a special name and cannot be used")
        return sname

    def cmd(self) -> str:
        """Command file string for this component."""
        return f"{self.model_type.upper()} sname='{self.sname}'"

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
