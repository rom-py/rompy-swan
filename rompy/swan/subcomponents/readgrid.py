"""Readgrid subcomponents."""
import logging
from typing import Literal, Optional
from abc import ABC

from pydantic import Field, model_validator, field_validator

from rompy.swan.types import GridOptions, IDLA
from rompy.swan.subcomponents.base import BaseSubComponent


logger = logging.getLogger(__name__)


class READGRID(BaseSubComponent, ABC):
    """SWAN grid reader abstract class.

    Notes
    -----

    File format identifier:

    * 1: Format according to BODKAR convention (a standard of the Ministry of
      Transport and Public Works in the Netherlands). Format string: (10X,12F5.0).
    * 5: Format (16F5.0), an input line consists of 16 fields of 5 places each.
    * 6: Format (12F6.0), an input line consists of 12 fields of 6 places each.
    * 8: Format (10F8.0), an input line consists of 10 fields of 8 places each.

    """

    model_type: Literal["readgrid", "READGRID"] = Field(
        default="readgrid", description="Model type discriminator"
    )
    grid_type: GridOptions | Literal["coordinates"] = Field(
        description="Type of the SWAN grid file",
    )
    fac: float = Field(
        default=1.0,
        description=(
            "SWAN multiplies all values that are read from file by `fac`. For instance "
            "if the values are given in unit decimeter, one should make `fac=0.1` to "
            "obtain values in m. To change sign use a negative `fac`"
        ),
        gt=0.0,
    )
    idla: IDLA = Field(
        default=1,
        description=(
            "Prescribes the order in which the values of bottom levels "
            "and other fields should be given in the file"
        ),
    )
    nhedf: int = Field(
        default=0,
        description=(
            "The number of header lines at the start of the file. The text in the "
            "header lines is reproduced in the print file created by SWAN . The file "
            "may start with more header lines than `nhedf` because the start of the "
            "file is often also the start of a time step and possibly also of a "
            "vector variable (each having header lines, see `nhedt` and `nhedvec`)"
        ),
        ge=0,
    )
    nhedvec: int = Field(
        default=0,
        description=(
            "For each vector variable: number of header lines in the file "
            "at the start of each component (e.g., x- or y-component)"
        ),
        ge=0,
    )
    format: Literal["free", "fixed", "unformatted"] = Field(
        default="free",
        description=(
            "File format, one of 'free', 'fixed' or 'unformatted'. If 'free', the "
            "file is assumed to use the FREE FORTRAN format. If 'fixed', the file is "
            "assumed to use a fixed format that must be specified by (only) one of "
            "'form' or 'idfm' arguments. Use 'unformatted' to read unformatted "
            "(binary) files (not recommended for ordinary use)"
        ),
    )
    form: Optional[str] = Field(
        default=None,
        description=(
            "A user-specified format string in Fortran convention, e.g., '(10X,12F5.0)'."
            "Only used if `format='fixed'`, do not use it if `idfm` is specified"
        ),
    )
    idfm: Optional[Literal[1, 5, 6, 8]] = Field(
        default=None,
        description=("File format identifier, only used if `format='fixed'`"),
    )

    @model_validator(mode="after")
    def check_format_definition(self) -> "READGRID":
        """Check the arguments specifying the file format are specified correctly."""
        if self.format == "free" and any([self.form, self.idfm]):
            logger.warn(f"FREE format, ignoring form={self.form} idfm={self.idfm}")
        elif self.format == "unformatted" and any([self.form, self.idfm]):
            logger.warn(
                f"UNFORMATTED format, ignoring form={self.form} idfm={self.idfm}"
            )
        elif self.format == "fixed" and not any([self.form, self.idfm]):
            raise ValueError(
                "FIXED format requires one of form or idfm to be specified"
            )
        elif self.format == "fixed" and all([self.form, self.idfm]):
            raise ValueError("FIXED format accepts only one of form or idfm")
        return self

    @property
    def format_repr(self):
        if self.format == "free":
            repr = "FREE"
        elif self.format == "fixed" and self.form:
            repr = f"FORMAT form='{self.form}'"
        elif self.format == "fixed" and self.idfm:
            repr = f"FORMAT idfm={self.idfm}"
        elif self.format == "unformatted":
            repr = "UNFORMATTED"
        return repr


class READCOORD(READGRID):
    """SWAN coordinates reader.

    .. code-block:: text

        READGRID COORDINATES [fac] 'fname' [idla] [nhedf] [nhedvec] FREE|FORMAT &
            ('form'|idfm)

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        @suppress
        from rompy.swan.subcomponents.readgrid import READCOORD

        readcoord = READCOORD(
            fac=1.0,
            fname="coords.txt",
            idla=3,
            format="free",
        )
        print(readcoord.render())

    """

    model_type: Literal["readcoord", "READCOORD"] = Field(
        default="readcoord", description="Model type discriminator"
    )
    grid_type: Literal["coordinates"] = Field(
        default="coordinates", description="Type of the SWAN grid file"
    )
    fname: str = Field(description="Name of the SWAN coordinates file")

    def cmd(self) -> str:
        repr = (
            f"READGRID COORDINATES fac={self.fac} fname='{self.fname}' "
            f"idla={self.idla} nhedf={self.nhedf} nhedvec={self.nhedvec} "
            f"{self.format_repr}"
        )
        return repr


class READINP(READGRID):
    """SWAN input grid reader.

    `READINP GRID_TYPE [fac] 'fname1'|SERIES 'fname2' [idla] [nhedf] ([nhedt]) [nhedvec] FREE|FORMAT ('form'|idfm)|UNFORMATTED`

    """

    model_type: Literal["readinp"] = Field(
        default="readinp", description="Model type discriminator"
    )
    grid_type: Optional[GridOptions] = Field(
        default=None, description="Type of the SWAN grid file"
    )
    fname1: str = Field(
        description="Name of the file with the values of the variable.",
    )
    fname2: Optional[str] = Field(
        default=None,
        description=(
            "Name of file that contains the names of the files where the variables "
            "are given when the SERIES option is used. These names are to be given in "
            "proper time sequence. SWAN reads the next file when the previous file "
            "end has been encountered. In these files the input should be given in "
            "the same format as in the above file 'fname1' (that implies that a file "
            "should start with the start of an input time step)."
        ),
    )
    nhedt: int = Field(
        default=0,
        description=(
            "Only if variable is time dependent: number of header lines in the file "
            "at the start of each time level. A time step may start with more header "
            "lines than `nhedt` because the variable may be a vector variable which "
            "has its own header lines (see `nhedvec`)."
        ),
        ge=0,
    )

    @field_validator("grid_type")
    @classmethod
    def set_undefined(cls, v: str | None) -> str:
        """Allow for undefined value so it can be redefined in INPGRID components."""
        if v is None:
            return "undefined"
        return v

    def cmd(self) -> str:
        repr = f"READINP {self.grid_type.upper()} fac={self.fac} fname1='{self.fname1}'"
        if self.fname2:
            repr += f" SERIES fname2='{self.fname2}'"
        repr += f" idla={self.idla} nhedf={self.nhedf} nhedt={self.nhedt} nhedvec={self.nhedvec} {self.format_repr}"
        return repr
