"""Base class for SWAN components.

How to subclass
---------------

- Define a new `kind` Literal type for the subclass
- Overwrite the __repr__ method to return the SWAN input file string

"""
from enum import Enum
from datetime import datetime, timedelta
from typing_extensions import Literal
from pydantic import BaseModel, root_validator

from rompy.core import RompyBaseModel


TIME_FORMATS = {
    1: "%Y%m%d.%H%M%S",
    2: "'%d-%b-%y %H:%M:%S'",
    3: "%m/%d/%y.%H:%M:%S",
    4: "%H:%M:%S",
    5: "%y/%m/%d %H:%M:%S'",
    6: "%y%m%d%H%M",
}


class BaseComponent(RompyBaseModel):
    """Base class for SWAN components.

    Parameters
    ----------
    kind : Literal["base"]
        Name of the component to help parsing and render as a comment in the cmd file.

    Behaviour
    ---------
    - Make all string input case-insensitive.
    - Define a header from parent classes names and the component kind.
    - Define a render method to render the component to a cmd string.

    """

    kind: Literal["base"]

    @root_validator(pre=True)
    def to_lowercase(cls, values):
        """Make all string input case-insensitive."""
        values = {k: v.lower() if isinstance(v, str) else v for k, v in values.items()}
        return values

    @property
    def header(self):
        """Define a header from parent classes names and the component kind."""
        s = " ".join([c.__name__ for c in self.__class__.__bases__] + [self.kind.upper()])
        return f"\n!{s.center(131, '-')}\n"

    def render(self):
        """Render the component to a string."""
        return f"{self.header}{self.__repr__()}\n"


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