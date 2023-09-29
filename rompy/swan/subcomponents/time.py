"""Time subcomponents."""
import logging
from datetime import datetime, timedelta
from typing import Literal, Optional
from pydantic import Field, field_validator

from rompy.swan.subcomponents.base import BaseSubComponent


logger = logging.getLogger(__name__)


TIME_FORMATS = {
    1: "%Y%m%d.%H%M%S",
    2: "'%d-%b-%y %H:%M:%S'",
    3: "%m/%d/%y.%H:%M:%S",
    4: "%H:%M:%S",
    5: "%y/%m/%d %H:%M:%S'",
    6: "%y%m%d%H%M",
}


class TIME(BaseSubComponent):
    """Time specification.

    .. code-block:: text

        [tbeg] [delt] SEC|MIN|HR|DAY

    Note
    ----
    **Format to render time specification**

    * 1: ISO-notation 19870530.153000
    * 2: (as in HP compiler) '30-May-87 15:30:00'
    * 3: (as in Lahey compiler) 05/30/87.15:30:00
    * 4: 15:30:00
    * 5: 87/05/30 15:30:00'
    * 6: as in WAM 8705301530

    Note
    ----
    **The datetime types can be specified as**

    * existing datetime object
    * int or float, assumed as Unix time, i.e. seconds (if >= -2e10 or <= 2e10) or
      milliseconds (if < -2e10 or > 2e10) since 1 January 1970.
    * ISO 8601 time string.


    Note
    ----
    **The timedelta type can be specified as**

    * existing timedelta object
    * int or float, assumed as seconds
    * ISO 8601 duration string, following formats work:

      * `[-][DD ][HH:MM]SS[.ffffff]`
      * `[±]P[DD]DT[HH]H[MM]M[SS]S` (ISO 8601 format for timedelta)

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.subcomponents.time import TIME
        import datetime
        time = TIME(
            tbeg=datetime.datetime(1990, 1, 1),
            tend=datetime.datetime(1990, 1, 7),
            delt=datetime.timedelta(minutes=30),
            deltfmt="min",
        )
        print(time.render())
        time = TIME(
            tbeg="2012-01-01T00:00:00",
            delt="PT1H",
            deltfmt="hr",
            tfmt=2,
            suffix="bl",
        )
        print(time.render())

    """

    model_type: Literal["time", "TIME"] = Field(
        default="time", description="Model type discriminator"
    )
    tbeg: datetime = Field(description="Begin time of the first field of the variable")
    delt: timedelta = Field(description="Time interval between fields")
    tend: Optional[datetime] = Field(
        default=None,
        description="End time of the last field of the variable",
    )
    tfmt: Literal[1, 2, 3, 4, 5, 6] = Field(
        default=1,
        description="Format to render time specification",
        validate_default=True,
    )
    deltfmt: Literal["sec", "min", "hr", "day"] = Field(
        default="sec",
        description="Format to render time interval specification",
    )
    suffix: str = Field(
        default="",
        description="Suffix to append to the variable name when rendering",
    )

    @field_validator("tfmt")
    @classmethod
    def set_time_format(cls, v: int) -> str:
        """Set the time format."""
        return TIME_FORMATS[v]

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

    def cmd(self) -> str:
        """Render TIME string."""
        repr = f"tbeg{self.suffix}={self.tbeg.strftime(self.tfmt)}"
        repr += f" delt{self.suffix}={self.delt_string}"
        if self.tend is not None:
            repr += f" tend{self.suffix}={self.tend.strftime(self.tfmt)}"
        return repr


class NONSTATIONARY(BaseSubComponent):
    """SWAN Nonstationary specification.

    .. code-block:: text

        NONSTATIONARY [tbeg] [delt] SEC|MIN|HR|DAY [tend]

    Notes
    -----

    Format to render time specification
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * 1: ISO-notation 19870530.153000
    * 2: (as in HP compiler) '30-May-87 15:30:00'
    * 3: (as in Lahey compiler) 05/30/87.15:30:00
    * 4: 15:30:00
    * 5: 87/05/30 15:30:00'
    * 6: as in WAM 8705301530

    The datetime types can be specified as
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * existing datetime object
    * int or float, assumed as Unix time, i.e. seconds (if >= -2e10 or <= 2e10) or
      milliseconds (if < -2e10 or > 2e10) since 1 January 1970.
    * ISO 8601 time string.

    The timedelta type can be specified as
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * existing timedelta object
    * int or float, assumed as seconds
    * ISO 8601 duration string, following formats work:

      * `[-][DD ][HH:MM]SS[.ffffff]`
      * `[±]P[DD]DT[HH]H[MM]M[SS]S` (ISO 8601 format for timedelta)

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.subcomponents.time import NONSTATIONARY
        nonstat = NONSTATIONARY(
            tbeg="2012-01-01T00:00:00",
            tend="2012-02-01T00:00:00",
            delt="PT1H",
            deltfmt="hr",
        )
        print(nonstat.render())
        import datetime
        nonstat = NONSTATIONARY(
            tbeg=datetime.datetime(1990, 1, 1),
            tend=datetime.datetime(1990, 1, 7),
            delt=datetime.timedelta(minutes=30),
            deltfmt="min",
        )
        print(nonstat.render())

    TODO: Remove this class and use TIME instead.

    """

    model_type: Literal["nonstationary", "NONSTATIONARY"] = Field(
        default="nonstationary", description="Model type discriminator"
    )
    tbeg: datetime = Field(description="Begin time of the first field of the variable")
    delt: timedelta = Field(description="Time interval between fields")
    tend: datetime = Field(description="End time of the last field of the variable")
    tfmt: Literal[1, 2, 3, 4, 5, 6] = Field(
        default=1,
        description="Format to render time specification",
        validate_default=True,
    )
    deltfmt: Literal["sec", "min", "hr", "day"] = Field(
        default="sec",
        description="Format to render time interval specification",
    )
    suffix: Optional[str] = Field(
        default=None, description="Suffix to append to the variable name when rendering"
    )

    @field_validator("tfmt")
    @classmethod
    def set_time_format(cls, v: int) -> str:
        """Set the time format."""
        return TIME_FORMATS[v]

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

    def cmd(self) -> str:
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
