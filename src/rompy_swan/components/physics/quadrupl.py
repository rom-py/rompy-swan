"""SWAN quadruplet interaction component.

This module contains the QUADRUPL component for configuring nonlinear quadruplet
wave interactions in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class QUADRUPL(BaseComponent):
    """Nonlinear quadruplet wave interactions.

    .. code-block:: text

        QUADRUPL [iquad] [lambda] [cnl4] [Csh1] [Csh2] [Csh3]

    With this option the user can influence the computation of nonlinear quadruplet
    wave interactions which are usually included in the computations. Can be
    de-activated with command OFF QUAD. Note that the DIA approximation of the
    quadruplet interactions is a poor approximation for long-crested waves and
    frequency resolutions that are deviating much more than 10% (see command CGRID).
    Note that DIA is usually updated per sweep, either semi-implicit (`iquad = 1`) or
    explicit (`iquad = 2`). However, when ambient current is included, the bounds of
    the directional sector within a sweep may be different for each frequency bin
    (particularly the higher frequencies are modified by the current). So there may be
    some overlap of frequency bins between the sweeps, implying non-conservation of
    wave energy. To prevent this the user is advised to choose the integration of DIA
    per iteration instead of per sweep, i.e. `iquad = 3`. If you want to speed up your
    computation a bit more, than the choice `iquad = 8` is a good choice.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import QUADRUPL
        quadrupl = QUADRUPL()
        print(quadrupl.render())
        kwargs = dict(
            iquad=3, lambd=0.25, cnl4=3.0e7, csh1=5.5, csh2=0.833333, csh3=-1.25
        )
        quadrupl = QUADRUPL(**kwargs)
        print(quadrupl.render())

    """

    model_type: Literal["quadrupl", "QUADRUPL"] = Field(
        default="quadrupl", description="Model type discriminator"
    )
    iquad: Optional[Literal[1, 2, 3, 8, 4, 51, 52, 53]] = Field(
        default=None,
        description=(
            "Numerical procedures for integrating the quadruplets: 1 = semi-implicit "
            "per sweep, 2 = explicit per sweep, 3 = explicit per iteration, "
            "8 = explicit per iteration, but with a more efficient implementation, "
            "4 = multiple DIA, 51 = XNL (deep water transfer), 52 = XNL (deep water "
            "transfer with WAM depth scaling), 53  XNL (finite depth transfer) (SWAN "
            "default: 2)"
        ),
    )
    lambd: Optional[float] = Field(
        default=None,
        description=(
            "Coefficient for quadruplet configuration in case of DIA "
            "(SWAN default: 0.25)"
        ),
    )
    cnl4: Optional[float] = Field(
        default=None,
        description=(
            "Proportionality coefficient for quadruplet interactions in case of DIA "
            "(SWAN default: 3.0e7"
        ),
    )
    csh1: Optional[float] = Field(
        default=None,
        description=(
            "Coefficient for shallow water scaling in case of DIA (SWAN default: 5.5)"
        ),
    )
    csh2: Optional[float] = Field(
        default=None,
        description=(
            "Coefficient for shallow water scaling in case of DIA "
            "(SWAN default: 0.833333)"
        ),
    )
    csh3: Optional[float] = Field(
        default=None,
        description=(
            "Coefficient for shallow water scaling in case of DIA (SWAN default: -1.25)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "QUADRUPL"
        if self.iquad is not None:
            repr += f" iquad={self.iquad}"
        if self.lambd is not None:
            repr += f" lambda={self.lambd}"
        if self.cnl4 is not None:
            repr += f" cnl4={self.cnl4}"
        if self.csh1 is not None:
            repr += f" csh1={self.csh1}"
        if self.csh2 is not None:
            repr += f" csh2={self.csh2}"
        if self.csh3 is not None:
            repr += f" csh3={self.csh3}"
        return repr
