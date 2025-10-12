"""SWAN output component."""

from typing import Annotated, Literal, Optional, Union

from pydantic import Field

from rompy_swan.subcomponents.output import ABS, REL, SPEC1D, SPEC2D
from rompy_swan.types import BlockOptions

from rompy_swan.components.output import BaseWrite


class TABLE(BaseWrite):
    """Write spatial distributions.

    .. code-block:: text

        TABLE 'sname' ->HEADER|NOHEADER|INDEXED 'fname'  < output > &
            (OUTPUT [tbegblk] [deltblk]) SEC|MIN|HR|DAY

    With this optional command the user indicates that for each location of the output
    location set 'sname' (see commands `POINTS`, `CURVE`, `FRAME` or `GROUP`) one or
    more variables should be written to a file. The keywords `HEADER` and `NOHEADER`
    determine the appearance of the table; the filename determines the destination of
    the data.

    Note
    ----
    **HEADER**:
    output is written in fixed format to file with headers giving name of variable
    and unit per column (numbers too large to be written will be shown as `****`.
    The number of header lines is 4.

    **NOHEADER**:
    output is written in floating point format to file and has no headers.

    **INDEXED**:
    output compatible with GIS tools such as ARCVIEW, ARCINFO, etc. The user should
    give two TABLE commands, one to produce one file with `XP` and `YP` as output
    quantities, the other with `HS`, `RTM01` or other output quantities.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import TABLE
        table = TABLE(
            sname="outpts",
            format="noheader",
            fname="./output_table.nc",
            output=["hsign", "hswell", "dir", "tps", "tm01", "watlev", "qp"],
            times=dict(tbeg="2012-01-01T00:00:00", delt="PT30M", dfmt="min"),
        )
        print(table.render())

    """

    model_type: Literal["table", "TABLE"] = Field(
        default="table", description="Model type discriminator"
    )
    format: Optional[Literal["header", "noheader", "indexed"]] = Field(
        default=None,
        description=(
            "Indicate if the table should be written to a file as a HEADER, NOHEADER "
            "or INDEXED table format (SWAN default: HEADER)"
        ),
    )
    output: list[BlockOptions] = Field(
        description="The output variables to output to block file",
        min_length=1,
    )

    @property
    def suffix(self) -> str:
        return "tbl"

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"TABLE sname='{self.sname}'"
        if self.format is not None:
            repr += f" {self.format.upper()}"
        repr += f" fname='{self.fname}'"
        for output in self.output:
            if len(self.output) > 1:
                repr += "\n"
            else:
                repr += " "
            repr += f"{output.upper()}"
        if self.times is not None:
            repr += f"\nOUTPUT {self.times.render()}"
        return repr


DIM_TYPE = Annotated[
    Union[SPEC1D, SPEC2D],
    Field(
        description="Choose between 1D or 2D spectra output",
        discriminator="model_type",
    ),
]
FREQ_TYPE = Annotated[
    Union[ABS, REL],
    Field(
        description="Choose between absolute or relative frequency spectra",
        discriminator="model_type",
    ),
]
