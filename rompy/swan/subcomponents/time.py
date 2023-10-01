"""Time subcomponents."""
import logging
from datetime import datetime, timedelta
from typing import Literal, Optional
from pydantic import Field, field_validator, model_validator

from rompy.swan.subcomponents.base import BaseSubComponent


logger = logging.getLogger(__name__)


class TIME(BaseSubComponent):
    """Time specification in SWAN.

    .. code-block:: text

        [time]

    Time is rendered in one of the following formats:

    * 1: ISO-notation 19870530.153000
    * 2: (as in HP compiler) '30-May-87 15:30:00'
    * 3: (as in Lahey compiler) 05/30/87.15:30:00
    * 4: 15:30:00
    * 5: 87/05/30 15:30:00'
    * 6: as in WAM 8705301530

    Note
    ----
    The `time` field can be specified as:

    * existing datetime object
    * int or float, assumed as Unix time, i.e. seconds (if >= -2e10 or <= 2e10) or
      milliseconds (if < -2e10 or > 2e10) since 1 January 1970.
    * ISO 8601 time string.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.subcomponents.time import TIME
        from datetime import datetime
        time = TIME(time=datetime(1990, 1, 1))
        print(time.render())
        time = TIME(time="2012-01-01T00:00:00", tfmt=2)
        print(time.render())

    """

    model_type: Literal["time", "TIME"] = Field(
        default="time", description="Model type discriminator"
    )
    time: datetime = Field(description="Datetime specification")
    tfmt: Literal[1, 2, 3, 4, 5, 6] = Field(
        default=1,
        description="Format to render time specification",
        validate_default=True,
    )

    @field_validator("tfmt")
    @classmethod
    def set_time_format(cls, v: int) -> str:
        """Set the time format to render."""
        time_format = {
            1: "%Y%m%d.%H%M%S",
            2: "'%d-%b-%y %H:%M:%S'",
            3: "%m/%d/%y.%H:%M:%S",
            4: "%H:%M:%S",
            5: "%y/%m/%d %H:%M:%S'",
            6: "%y%m%d%H%M",
        }
        return time_format[v]

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        return f"{self.time.strftime(self.tfmt)}"


class DELT(BaseSubComponent):
    """Time interval specification in SWAN.

    .. code-block:: text

        [delt] SEC|MIN|HR|DAY

    Note
    ----
    The `tdelta` field can be specified as:

    * existing timedelta object
    * int or float, assumed as seconds
    * ISO 8601 duration string, following formats work:

      * `[-][DD ][HH:MM]SS[.ffffff]`
      * `[±]P[DD]DT[HH]H[MM]M[SS]S` (ISO 8601 format for timedelta)

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.subcomponents.time import DELT
        from datetime import timedelta
        delt = DELT(delt=timedelta(minutes=30))
        print(delt.render())
        delt = DELT(delt="PT1H", dfmt="hr")
        print(delt.render())

    """

    model_type: Literal["tdelt", "DELT"] = Field(
        default="tdelt", description="Model type discriminator"
    )
    delt: timedelta = Field(description="Time interval")
    dfmt: Literal["sec", "min", "hr", "day"] = Field(
        default="sec",
        description="Format to render time interval specification",
    )

    @model_validator(mode="after")
    def to_time_unit(self) -> "DELT":
        """Convert interval value to the time unit specified."""
        delt_scaling = {"sec": 1, "min": 60, "hr": 3600, "day": 86400}
        self.delt = self.delt.total_seconds() / delt_scaling[self.dfmt]
        return self

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        return f"{self.delt} {self.dfmt.upper()}"


class TIMERANGE(BaseSubComponent):
    """Regular times specification.

    .. code-block:: text

        [tbeg] [delt] SEC|MIN|HR|DAY

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.subcomponents.time import TIMERANGE
        from datetime import datetime, timedelta
        times = TIMERANGE(
            tbeg=dict(time=datetime(1990, 1, 1)),
            tend=dict(time=datetime(1990, 1, 7)),
            delt=dict(delt=timedelta(minutes=30), dfmt="min"),
        )
        print(times.render())
        times = TIMERANGE(
            tbeg=dict(time="2012-01-01T00:00:00", tfmt=2),
            delt=dict(delt="PT1H", dfmt="hr"),
            suffix="blk",
        )
        print(times.render())

    """

    model_type: Literal["timerange", "TIMERANGE"] = Field(
        default="timerange", description="Model type discriminator"
    )
    tbeg: TIME = Field(description="Begin time of the first field of the variable")
    delt: DELT = Field(description="Time interval between fields")
    tend: Optional[TIME] = Field(
        default=None,
        description="End time of the last field of the variable",
    )
    suffix: str = Field(
        default="",
        description="Suffix to prepend to argument names when rendering",
    )

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        repr = f"tbeg{self.suffix}={self.tbeg.render()}"
        repr += f" delt{self.suffix}={self.delt.render()}"
        if self.tend is not None:
            repr += f" tend{self.suffix}={self.tend.render()}"
        return repr


class NONSTATIONARY(TIMERANGE):
    """Nonstationary time specification.

    .. code-block:: text

        NONSTATIONARY [tbeg] [delt] SEC|MIN|HR|DAY [tend]

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.subcomponents.time import NONSTATIONARY
        nonstat = NONSTATIONARY(
            tbeg=dict(time="2012-01-01T00:00:00"),
            tend=dict(time="2012-02-01T00:00:00"),
            delt=dict(delt="PT1H", dfmt="hr"),
        )
        print(nonstat.render())
        from datetime import datetime, timedelta
        nonstat = NONSTATIONARY(
            tbeg=dict(time=datetime(1990, 1, 1)),
            tend=dict(time=datetime(1990, 1, 7)),
            delt=dict(delt=timedelta(minutes=30), dfmt="min"),
            suffix="tbl",
        )
        print(nonstat.render())

    """

    model_type: Literal["nonstationary", "NONSTATIONARY"] = Field(
        default="nonstationary", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        repr = f"NONSTATIONARY {super().cmd()}"
        return repr


class STATIONARY(BaseSubComponent):
    """Stationary time specification.

    .. code-block:: text

        STATIONARY [time]

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.subcomponents.time import STATIONARY
        stat = STATIONARY(time=dict(time="2012-01-01T00:00:00"))
        print(stat.render())

    """

    model_type: Literal["stationary", "STATIONARY"] = Field(
        default="stationary", description="Model type discriminator"
    )
    time: TIME = Field(description="Time to which stationary run is to be made")

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        return f"STATIONARY time={self.time.render()}"
