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

from rompy_swan.components.output.write.block import BaseWrite

SPECIAL_NAMES = ["BOTTGRID", "COMPGRID", "BOUNDARY", "BOUND_"]


class NESTOUT(BaseWrite):
    """Write to 2D boundary spectra.

    .. code-block:: text

        NESTOUT 'sname' 'fname' (OUTPUT [tbegnst] [deltnst] ->SEC|MIN|HR|DAY)

    Write to data file two-dimensional action density spectra (relative frequency)
    along the boundary of a nested grid (see command NGRID) to be used in a subsequent
    SWAN run.

    Note
    ----
    Cannot be used in 1D-mode.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import NESTOUT
        out = NESTOUT(
            sname="outnest",
            fname="./nestout.swn",
            times=dict(tbeg="2012-01-01T00:00:00", delt="PT30M", dfmt="min"),
        )
        print(out.render())

    """

    model_type: Literal["nestout", "NESTOUT"] = Field(
        default="nestout", description="Model type discriminator"
    )

    @property
    def suffix(self) -> str:
        return "nst"

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"NESTOUT sname='{self.sname}' fname='{self.fname}'"
        if self.times is not None:
            repr += f" OUTPUT {self.times.render()}"
        return repr
