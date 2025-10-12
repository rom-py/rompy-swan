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


class QUANTITY(BaseComponent):
    """Define output settings.

    .. code-block:: text

        QUANTITY < output > 'short' 'long' [lexp] [hexp] [excv] [power] [ref] &
            [fswell] [fmin] [fmax] ->PROBLEMCOORD|FRAME

        Examples:
        ---------
        QUANTITY Xp hexp=100.
        QUANTITY HS TM01 RTMM10 excv=-9.
        QUANTITY HS TM02 FSPR fmin=0.03 fmax=0.5
        QUANTITY Hswell fswell=0.08
        QUANTITY Per short='Tm-1,0' power=0.
        QUANTITY Transp Force Frame

    With this command the user can influence:

    * The naming of output quantities
    * The accuracy of writing output quantities
    * The definition of some output quantities
    * Reference direction for vectors

    Note
    ----
    The following data are accepted only in combination with some specific quantities:

    * power
    * ref
    * fswell
    * fmin
    * fmax
    * PROBLEMCOORD
    * FRAME

    Note
    ----
    **PROBLEMCOORD**: Vector components are relative to the x- and y-axes of the
    problem coordinate system (see command `SET`):

    * Directions are counterclockwise relative to the positive x-axis of the problem
      coordinate system if Cartesian direction convention is used.
    * Directions are relative to North (clockwise) if Nautical direction convention is
      used.

    Note
    ----
    **FRAME**: If output is requested on sets created by command FRAME or
    automatically (see command `SET`) (`COMPGRID` or `BOTTGRID`):

    * Vector components are relative to the x- and y-axes of the frame coordinate
      system.
    * Directions are counterclockwise relative to the positive x-axis of the frame
      coordinate system if Cartesian direction convention is used.
    * Directions are relative to North (clockwise) if Nautical direction convention
      is used.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import QUANTITY
        quant = QUANTITY(output=["xp"], hexp=100)
        print(quant.render())
        quant = QUANTITY(output=["hsign", "tm01", "rtmm10"], excv=-9)
        print(quant.render())
        quant = QUANTITY(output=["hsign", "tm02", "fspr"], fmin=0.03, fmax=0.5)
        print(quant.render())
        quant = QUANTITY(output=["hsign"], fswell=0.08)
        print(quant.render())
        quant = QUANTITY(output=["per"], short="Tm-1,0", power=0)
        print(quant.render())
        quant = QUANTITY(output=["transp", "force"], coord="frame")
        print(quant.render())

    """

    model_type: Literal["quantity", "QUANTITY"] = Field(
        default="quantity", description="Model type discriminator"
    )
    output: list[BlockOptions] = Field(
        description="The output variables to define settings for",
        min_length=1,
    )
    short: Optional[str] = Field(
        default=None,
        description=(
            "Short name of the output quantity (e.g. the name in the heading of a "
            "table written by SWAN). If this option is not used, SWAN will use a "
            "realistic name"
        ),
        max_length=16,
    )
    long: Optional[str] = Field(
        default=None,
        description=(
            "Long name of the output quantity (e.g. the name in the heading of a "
            "block output written by SWAN). If this option is not used, SWAN will "
            "use a realistic name"
        ),
        max_length=16,
    )
    lexp: Optional[float] = Field(
        default=None,
        description="Lowest expected value of the output quantity",
    )
    hexp: Optional[float] = Field(
        default=None,
        description=(
            "Highest expected value of the output quantity; the highest expected "
            "value is used by SWAN to determine the number of decimals in a table "
            "with heading. So the `QUANTITY` command can be used in case the default "
            "number of decimals in a table is unsatisfactory"
        ),
    )
    excv: Optional[float] = Field(
        default=None,
        description=(
            "In case there is no valid value (e.g. wave height in a dry point) this "
            "exception value is written in a table or block output"
        ),
    )
    power: Optional[float] = Field(
        default=None,
        description=(
            "power `p` appearing in the definition of `PER`, `RPER` and `WLEN`. Note "
            "that the value for `power` given for `PER` affects also the value of "
            "`RPER`; the power for `WLEN` is independent of that of `PER` or `RPER` "
            "(SWAN default: 1)"
        ),
    )
    ref: Optional[str] = Field(
        default=None,
        description=(
            "Reference time used for the quantity `TSEC`. Default value: starting "
            "time of the first computation, except in cases where this is later than "
            "the time of the earliest input. In these cases, the time of the earliest "
            "input is used"
        ),
    )
    fswell: Optional[float] = Field(
        default=None,
        description=(
            "Upper limit of frequency range used for computing the quantity HSWELL "
            "(SWAN default: 0.1 Hz)"
        ),
    )
    noswll: Optional[int] = Field(
        default=None,
        description=("Number of swells to output for watershed quantities "),
    )
    fmin: Optional[float] = Field(
        default=None,
        description=(
            "Lower limit of frequency range used for computing integral parameters "
            "(SWAN Default: 0.0 Hz)"
        ),
    )
    fmax: Optional[float] = Field(
        default=None,
        description=(
            "Upper limit of frequency range used for computing integral parameters "
            "(SWAN default: 1000.0 Hz, acts as infinity)"
        ),
    )
    coord: Optional[Literal["problemcoord", "frame"]] = Field(
        default=None,
        description=(
            "Define if vectors and directions refer to the problem coordinate system "
            "('problemcoord') or sets created by command FRAME ('frame') "
            "(SWAN default: problemcoord)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "QUANTITY"
        for output in self.output:
            repr += f" {output.upper()}"
        if self.short is not None:
            repr += f" short='{self.short}'"
        if self.long is not None:
            repr += f" long='{self.long}'"
        if self.lexp is not None:
            repr += f" lexp={self.lexp}"
        if self.hexp is not None:
            repr += f" hexp={self.hexp}"
        if self.excv is not None:
            repr += f" excv={self.excv}"
        if self.power is not None:
            repr += f" power={self.power}"
        if self.ref is not None:
            repr += f" ref='{self.ref}'"
        if self.fswell is not None:
            repr += f" fswell={self.fswell}"
        if self.noswll is not None:
            repr += f" noswll={self.noswll}"
        if self.fmin is not None:
            repr += f" fmin={self.fmin}"
        if self.fmax is not None:
            repr += f" fmax={self.fmax}"
        if self.coord is not None:
            repr += f" {self.coord.upper()}"
        return repr

class QUANTITIES(BaseComponent):
    """Define output settings for multiple output.

    .. code-block:: text

        QUANTITY < output > ...
        QUANTITY < output > ...
        ..

    This component can be used to prescribe and render multiple QUANTITY components.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import QUANTITY, QUANTITIES
        q1 = QUANTITY(output=["xp"], hexp=100)
        q2 = QUANTITY(output=["hsign", "tm01", "rtmm10"], excv=-9)
        q3 = QUANTITY(output=["hsign", "tm02", "fspr"], fmin=0.03, fmax=0.5)
        q4 = QUANTITY(output=["hsign"], fswell=0.08)
        q5 = QUANTITY(output=["per"], short="Tm-1,0", power=0)
        q6 = QUANTITY(output=["transp", "force"], coord="frame")
        quantities = QUANTITIES(quantities=[q1, q2, q3, q4, q5, q6])
        print(quantities.render())

    """

    model_type: Literal["quantities", "QUANTITIES"] = Field(
        default="quantities", description="Model type discriminator"
    )
    quantities: list[QUANTITY] = Field(description="QUANTITY components")

    def cmd(self) -> list:
        repr = []
        for quantity in self.quantities:
            repr += [quantity.cmd()]
        return repr
