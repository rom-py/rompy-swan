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

from rompy_swan.components.output.locations.frame import BaseLocation

SPECIAL_NAMES = ["BOTTGRID", "COMPGRID", "BOUNDARY", "BOUND_"]


class GROUP(BaseLocation):
    """Output locations on subset of a grid.

    .. code-block:: text

        GROUP 'sname' SUBGRID [ix1] [ix2] [iy1] [iy2]

    With this optional command the user defines a group of output locations on a
    rectangular or curvilinear grid that is identical with (part of) the computational
    grid (rectilinear or curvilinear). Such a group may be convenient for the user to
    obtain output that is not affected by interpolation errors.

    The subgrid contains those points (`ix`,`iy`) of the computational grid for which:
    `ix1` <= `ix` <= `ix2` and `iy1` <= `iy` <= `iy2` (The origin of the computational
    grid is `ix=0`, `iy=0`)

    Limitations: `ix1>=0`, `ix2<=mxc`, `iy1>=0`, `iy2<=myc` (`mxc` and `myc` as
    defined in the command `CGRID` which should always precede this command `GROUP`)

    Note
    ----
    Cannot be used in 1D-mode or in case of unstructured grids.

    Note
    ----
    Regular and curvilinear grids are supported.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import GROUP
        loc = GROUP(sname="subgrid", ix1=20, iy1=0, ix2=50, iy2=100)
        print(loc.render())

    """

    model_type: Literal["group", "GROUP"] = Field(
        default="group", description="Model type discriminator"
    )
    ix1: int = Field(
        description="Lowest index of the computational grid in the ix-direction",
        ge=0,
    )
    iy1: int = Field(
        description="Lowest index of the computational grid in the iy-direction",
        ge=0,
    )
    ix2: int = Field(
        description="Highest index of the computational grid in the ix-direction",
    )
    iy2: int = Field(
        description="Highest index of the computational grid in the ix-direction",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"{super().cmd()}"
        repr += f" SUBGRID ix1={self.ix1} iy1={self.iy1} ix2={self.ix2} iy2={self.iy2}"
        return repr
