"""Base class for SWAN components.

How to subclass
---------------

- Define a new `kind` Literal type for the subclass
- Overwrite the __repr__ method to return the SWAN input file string

"""
import logging
from enum import Enum
from datetime import datetime, timedelta
from typing_extensions import Literal
from pydantic import BaseModel, root_validator, conint

from rompy.core import RompyBaseModel


logger = logging.getLogger(__name__)

TIME_FORMATS = {
    1: "%Y%m%d.%H%M%S",
    2: "'%d-%b-%y %H:%M:%S'",
    3: "%m/%d/%y.%H:%M:%S",
    4: "%H:%M:%S",
    5: "%y/%m/%d %H:%M:%S'",
    6: "%y%m%d%H%M",
}

class GridOptions(str, Enum):
    """Valid options for the input grid type."""
    bottom = "bottom"
    wlevel = "wlevel"
    current = "current"
    wind = "wind"
    friction = "friction"
    nplants = "nplants"
    turbvisc = "turbvisc"
    mudlayer = "mudlayer"
    aice = "aice"
    hice = "hice"
    hss = "hss"
    tss = "tss"


class BaseComponent(RompyBaseModel):
    """Base class for SWAN components.

    Parameters
    ----------
    type : Literal["base"]
        Name of the component to help parsing and render as a header in the cmd file.

    Behaviour
    ---------
    - Make all string input case-insensitive.
    - Define a header from parent classes names and the component type.
    - Define a render method to render the component to a cmd string.

    """

    type: Literal["base"]

    @root_validator(pre=True)
    def to_lowercase(cls, values):
        """Make all string input case-insensitive."""
        values = {k: v.lower() if isinstance(v, str) else v for k, v in values.items()}
        return values

    @property
    def header(self):
        """Define a header from parent classes names and the component type."""
        s = " ".join([c.__name__ for c in self.__class__.__bases__] + [self.type.upper()])
        return f"\n!{s.center(131, '-')}\n"

    def render(self):
        """Render the component to a string."""
        return f"{self.header}{self.__repr__()}\n"


class READGRID(BaseModel):
    """SWAN grid file.

    Parameters:
    -----------

    kind : Literal["readgrid"]
        Name of the component to help parsing and render as a comment in the cmd file.
    gridtype: GridOptions
        Type of the SWAN grid file.
    fac:
    fname: str
        Name of the SWAN grid file.
    idla:
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
        lines, see below, `nhedt` and `nhedvec`).
    nhedt: int
        Only if variable is time dependent: number of header lines in the file at the
        start of each time level. A time step may start with more header lines than
        `nhedt` because the variable may be a vector variable which has its own header
        lines (see below `nhedvec`).
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
    kind: Literal["readgrid"]
    gridtype: str
    fname: str
    fname1: str | None = None
    fname2: str | None = None
    idla: conint(ge=1, le=6) = 1
    nhedf: conint(ge=0) = 0
    nhedt: conint(ge=0) | None = None
    nhedvec: conint(ge=0) | None = None
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
    pass


class READINP(READGRID):
    pass


class NONSTATIONARY(BaseModel):
    """SWAN input grid.

    Parameters
    ----------
    kind : Literal["nonstationary"]
        Name of the component to help parsing and render as a comment in the cmd file.
    tbeg: datetime
        Begin time of the first field of the variable.
    delt:
        Time interval between fields.
    tend: datetime
        End time of the last field of the variable.
    tfmt: int
        Format to render time specification:
        - 1 : ISO-notation 19870530.153000
        - 2 : (as in HP compiler) '30-May-87 15:30:00'
        - 3 : (as in Lahey compiler) 05/30/87.15:30:00
        - 4 : 15:30:00
        - 5 : 87/05/30 15:30:00'
        - 6 : as in WAM 8705301530
    deltfmt: str:
        Format to render time interval specification.
    suffix: str | None = None
        Suffix to append to the variable name when rendering the nonstationray string.

    Notes
    -----
    The datetime types can be specified as:
    - existing datetime object
    - int or float, assumed as Unix time, i.e. seconds (if >= -2e10 or <= 2e10) or
      milliseconds (if < -2e10 or > 2e10) since 1 January 1970.
    - ISO 8601 time string.

    The timedelta type can be specified as:
    - existing timedelta object
    - int or float, assumed as seconds
    - ISO 8601 duration string, following formats work:
      [-][DD ][HH:MM]SS[.ffffff]
      [±]P[DD]DT[HH]H[MM]M[SS]S (ISO 8601 format for timedelta)

    """

    kind: Literal["nonstationary"] = "nonstationary"
    tbeg: datetime
    delt: timedelta
    tend: datetime
    tfmt: Literal[1, 2, 3, 4, 5, 6] = 1
    deltfmt: Literal["sec", "min", "hr", "day"] = "sec"
    suffix: str | None = None

    @root_validator
    def set_time_format(cls, values):
        """Set the time format."""
        values["tfmt"] = TIME_FORMATS[values.get("tfmt")]
        return values

    @property
    def delt_string(self):
        """Return the timedelta as a string."""
        dt = self.delt.total_seconds()
        if self.deltfmt == "min":
            dt /= 60
        elif self.deltfmt == "hr":
            dt /= 3600
        elif self.deltfmt == "day":
            dt /= 86400
        return f"{dt} {self.deltfmt.upper()}"

    def __repr__(self):
        """Render NONSTATIONARY string."""
        repr = "NONSTATIONARY"
        if self.suffix is not None:
            repr += f" tbeg{self.suffix}={self.tbeg.strftime(self.tfmt)}"
            repr += f" delt{self.suffix}={self.delt_string}"
            repr += f" tend{self.suffix}={self.tend.strftime(self.tfmt)}"
        else:
            repr += f" {self.tbeg.strftime(self.tfmt)}"
            repr += f" {self.delt_string}"
            repr += f" {self.tend.strftime(self.tfmt)}"
        return repr

    def render(self):
        return self.__repr__()