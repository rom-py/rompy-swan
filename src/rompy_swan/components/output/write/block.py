"""SWAN output component."""

from typing import Literal, Optional

from pydantic import Field, field_validator, model_validator

from rompy_swan.components.base import MultiComponents
from rompy_swan.components.output.write import BaseWrite
from rompy_swan.types import IDLA, BlockOptions


class BLOCK(BaseWrite):
    """Write spatial distributions.

    .. code-block:: text

        BLOCK 'sname' ->HEADER|NOHEADER 'fname' (LAYOUT [idla]) < output > &
            [unit] (OUTPUT [tbegblk] [deltblk]) SEC|MIN|HR|DAY

    With this optional command the user indicates that one or more spatial
    distributions should be written to a file.

    Note
    ----
    The SWAN special frames 'BOTTGRID' or 'COMPGRID' can be set with the `sname` field.

    Note
    ----
    The text of the header indicates run identification (see command `PROJECT`), time,
    frame or group name ('sname'), variable and unit. The number of header lines is 8.

    Note
    ----
    Cannot be used in 1D-mode.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import BLOCK
        block = BLOCK(sname="outgrid", fname="./depth-frame.nc", output=["depth"])
        print(block.render())
        block = BLOCK(
            sname="COMPGRID",
            header=False,
            fname="./output-grid.nc",
            idla=3,
            output=["hsign", "hswell", "dir", "tps", "tm01", "watlev", "qp"],
            times=dict(
                tbeg="2012-01-01T00:00:00",
                delt="PT30M",
                tfmt=1,
                dfmt="min",
                suffix="",
            )
        )
        print(block.render())

    """

    model_type: Literal["block", "BLOCK"] = Field(
        default="block", description="Model type discriminator"
    )
    header: Optional[bool] = Field(
        default=None,
        description=(
            "Indicate if the output should be written to a file with header lines "
            "(SWAN default: True)"
        ),
    )
    idla: Optional[IDLA] = Field(
        default=None,
        description=(
            "Prescribe the lay-out of the output to file (supported options here are "
            "1, 3, 4). Option 4 is recommended for postprocessing an ASCII file by "
            "MATLAB, however option 3 is recommended in case of binary MATLAB output "
            "(SWAN default: 1)"
        ),
    )
    output: list[BlockOptions] = Field(
        description="The output variables to output to block file",
        min_length=1,
    )
    unit: Optional[float] = Field(
        default=None,
        description=(
            "Controls the scaling of the output. The program divides computed values "
            "by `unit` before writing to file, so the user should multiply the "
            "written value by `unit` to obtain the proper value. By default, if "
            "HEADER is selected, value is written as a 5 position integer. SWAN takes "
            "`unit` such that the largest number occurring in the block can be "
            "printed. If NOHEADER is selected, values are printed in floating-point "
            "format by default (`unit=1`)"
        ),
    )

    @field_validator("idla")
    @classmethod
    def validate_idla(cls, idla: IDLA) -> IDLA:
        if idla is not None and idla not in (1, 3, 4):
            raise ValueError(
                f"Only IDLA options (1, 3, 4) are supported in BLOCK, got {idla}"
            )
        return idla

    @property
    def suffix(self) -> str:
        return "blk"

    @property
    def _header(self) -> str:
        """Render the header instruction."""
        if self.header:
            return "HEADER"
        else:
            return "NOHEADER"

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"BLOCK sname='{self.sname}'"
        if self.header is not None:
            repr += f" {self._header}"
        repr += f" fname='{self.fname}'"
        if self.idla is not None:
            repr += f" LAYOUT idla={self.idla}"
        for output in self.output:
            if len(self.output) > 1:
                repr += "\n"
            else:
                repr += " "
            repr += f"{output.upper()}"
        if self.unit is not None:
            repr += f"\nunit={self.unit}"
        if self.times is not None:
            repr += f"\nOUTPUT {self.times.render()}"
        return repr


class BLOCKS(MultiComponents):
    """Write multiple spatial distributions.

    .. code-block:: text

        BLOCK 'sname' ->HEADER|NOHEADER 'fname1' (LAYOUT [idla]) < output > &
            [unit] (OUTPUT [tbegblk] [deltblk]) SEC|MIN|HR|DAY
        BLOCK 'sname' ->HEADER|NOHEADER 'fname2' (LAYOUT [idla]) < output > &
            [unit] (OUTPUT [tbegblk] [deltblk]) SEC|MIN|HR|DAY
        ..

    This component can be used to prescribe and render multiple BLOCK components.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import BLOCK, BLOCKS
        block1 = BLOCK(sname="outgrid", fname="./depth.txt", output=["depth"])
        block2 = BLOCK(sname="outgrid", fname="./output.nc", output=["hsign", "hswell"])
        blocks = BLOCKS(components=[block1, block2])
        print(blocks.render())

    """

    model_type: Literal["blocks"] = Field(
        default="blocks", description="Model type discriminator"
    )
    components: list[BLOCK] = Field(description="BLOCK components")

    @property
    def sname(self) -> list[str]:
        return [component.sname for component in self.components]
