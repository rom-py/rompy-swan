"""SWAN output component."""

from typing import Literal

from pydantic import Field


from rompy_swan.components.output.write import BaseWrite


class NESTOUT(BaseWrite):
    """Write to 2D boundary spectra.

    .. code-block:: text

        NESTOUT 'sname' 'fname' (OUTPUT [tbegnst] [deltnst] ->SEC|MIN|HR|DAY)

    Write to data file two-dimensional action density spectra (relative frequency)
    along the boundary of a nested grid (see command NGRID) to be used in a subsequent
    SWAN run.

    Note
    ----
    Cannot be used in 1D-mode.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import NESTOUT
        out = NESTOUT(
            sname="outnest",
            fname="./nestout.swn",
            times=dict(tbeg="2012-01-01T00:00:00", delt="PT30M", dfmt="min"),
        )
        print(out.render())

    """

    model_type: Literal["nestout", "NESTOUT"] = Field(
        default="nestout", description="Model type discriminator"
    )

    @property
    def suffix(self) -> str:
        return "nst"

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"NESTOUT sname='{self.sname}' fname='{self.fname}'"
        if self.times is not None:
            repr += f" OUTPUT {self.times.render()}"
        return repr
