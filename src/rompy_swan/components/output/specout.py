"""SWAN output component."""

from typing import Annotated, Literal, Optional, Union

from pydantic import Field

from rompy_swan.subcomponents.output import ABS, REL, SPEC1D, SPEC2D

from rompy_swan.components.output import BaseWrite

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


class SPECOUT(BaseWrite):
    """Write to data file the wave spectra.

    .. code-block:: text

        SPECOUT 'sname' SPEC1D|->SPEC2D ->ABS|REL 'fname' &
            (OUTPUT [tbeg] [delt] SEC|MIN|HR|DAY)

    With this optional command the user indicates that for each location of the output
    location set 'sname' (see commands `POINTS`, `CURVE`, `FRAME` or `GROUP`) the 1D
    or 2D variance / energy (see command `SET`) density spectrum (either the relative
    frequency or the absolute frequency spectrum) is to be written to a data file.

    Note
    ----
    This write command supports the following location types: `POINTS`, `CURVE`,
    `FRAME` and `GROUP`.

    Note
    ----
    This output file can be used for defining boundary conditions for subsequent SWAN
    runs (command `BOUNDSPEC`).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import SPECOUT
        out = SPECOUT(sname="outpts", fname="./specout.swn")
        print(out.render())
        out = SPECOUT(
            sname="outpts",
            dim=dict(model_type="spec2d"),
            freq=dict(model_type="rel"),
            fname="./specout.nc",
            times=dict(tbeg="2012-01-01T00:00:00", delt="PT30M", dfmt="min"),
        )
        print(out.render())

    """

    model_type: Literal["specout", "SPECOUT"] = Field(
        default="specout", description="Model type discriminator"
    )
    dim: Optional[DIM_TYPE] = Field(default=None)
    freq: Optional[FREQ_TYPE] = Field(default=None)

    @property
    def suffix(self) -> str:
        return "spc"

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"SPECOUT sname='{self.sname}'"
        if self.dim is not None:
            repr += f" {self.dim.render()}"
        if self.freq is not None:
            repr += f" {self.freq.render()}"
        repr += f" fname='{self.fname}'"
        if self.times is not None:
            repr += f" OUTPUT {self.times.render()}"
        return repr
