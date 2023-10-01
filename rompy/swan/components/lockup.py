"""Model lockup components."""
import logging
from typing import Any, Literal, Optional, Union, Annotated
from pydantic import field_validator, model_validator, Field, FieldValidationInfo

from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.time import STATIONARY, NONSTATIONARY


logger = logging.getLogger(__name__)


TIMES_TYPE = Union[STATIONARY, NONSTATIONARY]


class COMPUTE(BaseComponent):
    """Start SWAN computation.

    .. code-block:: text

        COMPUTE STATIONARY|NONSTATIONARY

    If the SWAN mode is stationary (see command `MODE`), then only the command
    `COMPUTE` should be given here.

    If the SWAN mode is nonstationary (see command `MODE`), then the computation can
    be:

    * stationary (at the specified time: option STATIONARY here).
    * nonstationary (over the specified period of time.

    To verify input to SWAN (e.g., all input fields such as water depth, wind fields,
    etc), SWAN can be run without computations (that is: zero iterations by using
    command `NUM ACCUR MXITST=0`).

    In the case `MODE NONSTATIONARY` several commands COMPUTE can appear, where the
    wave state at the end of one computation is used as initial state for the next one,
    unless a command `INIT` appears in between the two COMPUTE commands. This enables
    the user to make a stationary computation to obtain the initial state for a
    nonstationary computation and/or to change the computational time step during a
    computation, to change a boundary condition etc. This also has the advantage of not
    using a hotfile since, it can be very large in size.

    For small domains, i.e. less than 100 km or 1 deg, a stationary computation is
    recommended. Otherwise, a nonstationary computation is advised.

    For a nonstationary computation, a time step of at most 10 minutes is advised (when
    you are choosing a time step larger than 10 minutes, the action density limiter
    (see command `NUM`) becomes probably a part of the physics).

    Also, the time step should be chosen such that the Courant number is smaller than
    10 for the fastest (or dominant) wave. Otherwise, a first order upwind scheme is
    recommended in that case; see command `PROP BSBT`. If you want to run a high
    resolution model with a very large time step, e.g. 1 hour, you may apply multiple
    COMPUT STAT commands. For a small time step (<= 10 minutes), no more than 1
    iteration per time step is recommended (see command `NUM ... NONSTAT mxitns`).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.components.lockup import COMPUTE
        comp = COMPUTE()
        print(comp.render())
        comp = COMPUTE(
            times=dict(
                model_type="stationary",
                time=dict(time="1990-01-01T00:00:00", tfmt=2),
            ),
        )
        print(comp.render())
        comp = COMPUTE(
            times=dict(
                model_type="nonstationary",
                tbeg=dict(time="1990-01-01T00:00:00", tfmt=1),
                tend=dict(time="1990-02-01T00:00:00", tfmt=1),
                delt=dict(delt="PT1H", dfmt="hr"),
            ),
        )
        print(comp.render())

    """

    model_type: Literal["compute", "COMPUTE"] = Field(
        default="compute", description="Model type discriminator"
    )
    times: Optional[TIMES_TYPE] = Field(
        default=None,
        description="Times for the stationary or nonstationary computation",
        discriminator="model_type",
    )

    @field_validator("times")
    @classmethod
    def validate_times(cls, times: TIMES_TYPE) -> TIMES_TYPE:
        if isinstance(times, NONSTATIONARY):
            times.suffix="c"
        return times

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "COMPUTE"
        if self.times is not None:
            repr += f" {self.times.render()}"
        return repr


class HOTFILE(BaseComponent):
    """Write intermediate results.

    .. code-block:: text

        HOTFILE 

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.components.lockup import HOTFILE
        hotfile = HOTFILE()
        print(hotfile.render())

    """

    model_type: Literal["hotfile", "HOTFILE"] = Field(
        default="hotfile", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        return "HOTFILE"


class STOP(BaseComponent):
    """Write intermediate results.

    .. code-block:: text

        STOP 

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.components.lockup import STOP
        stop = STOP()
        print(stop.render())

    """

    model_type: Literal["stop", "STOP"] = Field(
        default="stop", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        return "STOP"


class LOCKUP(BaseComponent):
    """Lockup group component.

    .. code-block:: text

        COMPUTE
        HOTFILE
        STOP

    TODO: Ensure commands can be mixed and matched.

    """

    model_type: Literal["lockup", "LOCKUP"] = Field(
        default="lockup", description="Model type discriminator"
    )

    def cmd(self) -> list:
        """Command file strings for this component."""
        return []