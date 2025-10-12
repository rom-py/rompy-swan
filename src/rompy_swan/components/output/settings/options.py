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


class OUTPUT_OPTIONS(BaseComponent):
    """Set format of output.

    .. code-block:: text

        OUTPUT OPTIons 'comment' (TABLE [field]) (BLOCK [ndec] [len]) (SPEC [ndec])

    This command enables the user to influence the format of block, table and spectral
    output.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import OUTPUT_OPTIONS
        opts = OUTPUT_OPTIONS(
            comment="!", field=10, ndec_block=4, len=20, ndec_spec=6,
        )
        print(opts.render())

    """

    model_type: Literal["block", "BLOCK"] = Field(
        default="block", description="Model type discriminator"
    )
    comment: Optional[str] = Field(
        default=None,
        description=(
            "Comment character used in comment lines in the output (SWAN default: %)"
        ),
        min_length=1,
        max_length=1,
    )
    field: Optional[int] = Field(
        default=None,
        description="Length of one data field in a table (SWAN default: 12)",
        ge=8,
        le=16,
    )
    ndec_block: Optional[int] = Field(
        default=None,
        description="Number of decimals in block output (SWAN default: 4)",
        ge=0,
        le=9,
    )
    len: Optional[int] = Field(
        default=None,
        description="Number of data on one line of block output (SWAN default: 6)",
        ge=1,
        le=9999,
    )
    ndec_spec: Optional[int] = Field(
        default=None,
        description="Number of decimals in spectra output (SWAN default: 4)",
        ge=0,
        le=9,
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "OUTPUT OPTIONS"
        if self.comment is not None:
            repr += f" comment='{self.comment}'"
        if self.field is not None:
            repr += f" TABLE field={self.field}"
        if self.ndec_block is not None or self.len is not None:
            repr += " BLOCK"
            if self.ndec_block is not None:
                repr += f" ndec={self.ndec_block}"
            if self.len is not None:
                repr += f" len={self.len}"
        if self.ndec_spec is not None:
            repr += f" SPEC ndec={self.ndec_spec}"
        return repr
