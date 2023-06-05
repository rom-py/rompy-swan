"""Readgrid subcomponents."""
import logging
from typing_extensions import Literal
from abc import ABC

from pydantic import root_validator, conint, confloat

from rompy.swan.types import GridOptions
from rompy.swan.subcomponents.base import BaseSubComponent

logger = logging.getLogger(__name__)


class READGRID(BaseSubComponent, ABC):
    """SWAN grid reader base class.

    Parameters:
    -----------
    model_type: Literal["readgrid"]
        Model type discriminator.
    grid_type: GridOptions
        Type of the SWAN grid file.
    fac: float
        SWAN multiplies all values that are read from file by `fac`. For instance if
        the values are given in unit decimeter, one should make `fac=0.1` to obtain
        values in m. To change sign use a negative `fac`.
    idla: int
        prescribes the order in which the values of bottom levels and other fields
        should be given in the file:
        - 1: SWAN reads the map from left to right starting in the upper-left-hand
          corner of the map (it is assumed that the x-axis of the grid is pointing
          to the right and the y-axis upwards). A new line in the map should start on
          a new line in the file.
        - 2: As `1` but a new line in the map need not start on a new line in the file.
        - 3: SWAN reads the map from left to right starting in the lower-left-hand corner
          of the map. A new line in the map should start on a new line in the file.
        - 4: As `3` but a new line in the map need not start on a new line in the file.
        - 5: SWAN reads the map from top to bottom starting in the lower-left-hand corner
          of the map. A new column in the map should start on a new line in the file.
        - 6: As `5` but a new column in the map need not start on a new line in the file.
    nhedf: int
        The number of header lines at the start of the file. The text in the header
        lines is reproduced in the print file created by SWAN . The file may start with
        more header lines than `nhedf` because the start of the file is often also the
        start of a time step and possibly also of a vector variable (each having header
        lines, see `nhedt` and `nhedvec`).
    nhedvec: int
        For each vector variable: number of header lines in the file at the start of
        each component (e.g., x- or y-component).
    format: str
        File format, one of `"free"`, `"fixed"` or `"unformatted"`. If `"free"`, the
        file is assumed to use the FREE FORTRAN format. If `"fixed"`, the file is
        assumed to use a fixed format that must be specified by (only) one of `form` or
        `idfm` arguments. Use `"unformatted"` to read unformatted (binary) files
        (not recommended for ordinary use).
    form: str
        A user-specified format string in Fortran convention, e.g., '(10X,12F5.0)'.
        Only used if `format="fixed"`, do not use it if `idfm` is specified.
    idfm: int
        File format identifier, only used if `format="fixed"`:
        - 1: Format according to BODKAR convention (a standard of the Ministry of
          Transport and Public Works in the Netherlands). Format string: (10X,12F5.0).
        - 5: Format (16F5.0), an input line consists of 16 fields of 5 places each.
        - 6: Format (12F6.0), an input line consists of 12 fields of 6 places each.
        - 8: Format (10F8.0), an input line consists of 10 fields of 8 places each.

    """
    model_type: Literal["readgrid"] = "readgrid"
    grid_type: GridOptions | Literal["coordinates"]
    fac: confloat(gt=0.0) = 1.0
    idla: conint(ge=1, le=6) = 1
    nhedf: conint(ge=0) = 0
    nhedvec: conint(ge=0) = 0
    format: Literal["free", "fixed", "unformatted"] = "free"
    form: str | None = None
    idfm: Literal[1, 5, 6, 8] | None = None

    @root_validator
    def check_format_definition(cls, values: dict) -> dict:
        """Check the arguments specifying the file format are specified correctly."""
        format = values.get("format")
        form = values.get("form")
        idfm = values.get("idfm")
        if format == "free" and any([form, idfm]):
            logger.warn(f"FREE format specified, ignoring form={form} idfm={idfm}")
        elif format == "unformatted" and any([form, idfm]):
            logger.warn(f"UNFORMATTED format specified, ignoring form={form} idfm={idfm}")
        elif format == "fixed" and not any([form, idfm]):
            raise ValueError("FIXED format requires one of form or idfm to be specified")
        elif format == "fixed" and all([form, idfm]):
            raise ValueError("FIXED format accepts only one of form or idfm")
        return values

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

    `READGRID COORDINATES [fac] 'fname' [idla] [nhedf] [nhedvec] FREE|FORMAT ('form'|idfm)`

    parameters
    ----------
    model_type: Literal["readcoord"]
        Model type discriminator.
    grid_type: Literal["coordinates"]
        Type of the SWAN grid file.
    fname: str
        Name of the SWAN coordinates file.

    """
    model_type: Literal["readcoord"] = "readcoord"
    grid_type: Literal["coordinates"] = "coordinates"
    fname: str

    @root_validator
    def check_arguments(cls, values: dict) -> dict:
        """A few checks to restrict input types from parent class."""
        for key in ["nhedt"]:
            if values.get(key):
                raise ValueError(f"{key} is not allowed for READCOORD")
        return values

    def cmd(self):
        repr = (
            f"READGRID COORDINATES fac={self.fac} fname='{self.fname}' "
            f"idla={self.idla} nhedf={self.nhedf} nhedvec={self.nhedvec} {self.format_repr}"
        )
        return repr


class READINP(READGRID):
    """SWAN input grid reader.

    `READINP GRID_TYPE [fac] 'fname1'|SERIES 'fname2' [idla] [nhedf] ([nhedt]) [nhedvec] FREE|FORMAT ('form'|idfm)|UNFORMATTED`

    parameters
    ----------
    model_type: Literal["readinp"]
        Model type discriminator.
    grid_type: GridOptions | None
        Type of the SWAN grid file.
    fname1: str
        Name of the file with the values of the variable.
    fname2: str | None
        Name of file that contains the names of the files where the variables are
        given when the SERIES option is used. These names are to be given in proper
        time sequence. SWAN reads the next file when the previous file end has been
        encountered. In these files the input should be given in the same format as in
        the above file 'fname1' (that implies that a file should start with the start
        of an input time step).
    nhedt: int
        Only if variable is time dependent: number of header lines in the file at the
        start of each time level. A time step may start with more header lines than
        `nhedt` because the variable may be a vector variable which has its own header
        lines (see `nhedvec`).

    """
    model_type: Literal["readinp"] = "readinp"
    grid_type: GridOptions | None = None
    fname1: str
    fname2: str | None = None
    nhedt: conint(ge=0) = 0

    @root_validator
    def check_arguments(cls, values: dict) -> dict:
        if values.get("grid_type") is None:
            values["grid_type"] = "undefined"
        return values

    def cmd(self):
        repr = (
            f"READINP {self.grid_type.upper()} fac={self.fac} fname1='{self.fname1}'"
        )
        if self.fname2:
            repr += f" SERIES fname2='{self.fname2}'"
        repr += f" idla={self.idla} nhedf={self.nhedf} nhedt={self.nhedt} nhedvec={self.nhedvec} {self.format_repr}"
        return repr
