"""SWAN numerics subcomponents."""
from typing import Annotated, Literal, Optional
from pydantic import field_validator, Field, model_validator
from abc import ABC
from pydantic_numpy.typing import Np2DArray
import numpy as np

from rompy.swan.subcomponents.base import BaseSubComponent


class BSBT(BaseSubComponent):
    """BSBT first order propagation scheme.

    .. code-block:: text

        BSTB

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        @suppress
        from rompy.swan.subcomponents.numerics import BSBT

        scheme = BSBT()
        print(scheme.render())

    """

    model_type: Literal["bsbt", "BSBT"] = Field(
        default="bsbt", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        return "BSBT"


class GSE(BaseSubComponent):
    """Garden-sprinkler effect.

    .. code-block:: text

        GSE [waveage] Sec|MIn|HR|DAy

    Garden-sprinkler effect is to be counteracted in the S&L propagation scheme
    (default for nonstationary regular grid computations) or in the propagation
    scheme for unstructured grids by adding a diffusion term to the basic equation.
    This may affect the numerical stability of SWAN.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        @suppress
        from rompy.swan.subcomponents.numerics import GSE

        scheme = GSE(waveage=1, units="day")
        print(scheme.render())

    """

    model_type: Literal["gse", "GSE"] = Field(
        default="gse", description="Model type discriminator"
    )
    waveage: Optional[float] = Field(
        default=None,
        description=(
            "The time interval used to determine the diffusion which counteracts the "
            "so-called garden-sprinkler effect. The default value of `waveage` is "
            "zero, i.e. no added diffusion. The value of `waveage` should correspond "
            "to the travel time of the waves over the computational region."
        ),
    )
    units: Literal["sec", "min", "hr", "day"] = Field(
        default="hr", description="Units for waveage",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "GSE"
        if self.waveage is not None:
            repr += f" waveage={self.waveage} {self.units.upper()}"
        return repr


class STOPC(BaseSubComponent):
    """Terminating the iterative procedure.

    .. code-block:: text

        STOPC [dabs] [drel] [curvat] [npnts] ->STAT|NONSTAT [limiter]

    With this option the user can influence the criterion for terminating the iterative
    procedure in the SWAN computations (both stationary and nonstationary). The
    criterion make use of the second derivative, or curvature, of the iteration curve
    of the significant wave height. As the solution of a simulation approaches full
    convergence, the curvature of the iteration curve will tend to zero. SWAN stops the
    process if the relative change in Hs from one iteration to the next is less than
    `drel` and the curvature of the iteration curve of Hs normalized with Hs is less
    than `curvat` or the absolute change in Hs from one iteration to the next is less
    than `dabs`. Both conditions need to be fulfilled in more than fraction `npnts`% of
    all wet grid points.

    With respect to the QC modelling, another stopping criteria will be employed.
    Namely, SWAN stops the iteration process if the absolute change in Hs from one
    iterate to another is less than `dabs` * Hinc, where Hinc is the representative
    incident wave height, or the relative change in Hs from one to the next iteration
    is less than `drel`. These criteria must be fulfilled in more than `npnts`% of
    all active, well-defined points.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        @suppress
        from rompy.swan.subcomponents.numerics import STOPC

        stop = STOPC()
        print(stop.render())

    """

    model_type: Literal["stopc", "STOPC"] = Field(
        default="stopc", description="Model type discriminator"
    )
    dabs: Optional[float] = Field(
        default=None,
        description=(
            "Maximum absolute change in Hs from one iteration to the next "
            "(SWAN default: 0.005 [m] or 0.05 [-] in case of QC model)"
        ),
    )
    drel: Optional[float] = Field(
        default=None,
        description=(
            "Maximum relative change in Hs from one iteration to the next "
            "(SWAN default: 0.01 [-])"
        ),
    )
    curvat: Optional[float] = Field(
        default=None,
        description=(
            "Maximum curvature of the iteration curve of Hs normalised with Hs "
            "(SWAN default: 0.005 [-] (not used in the QC model))"
        ),
    )
    npts
    STAT|NONSTAT
    limiter

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "STOPC"
        if self.dabs is not None:
            repr += f" dabs={self.dabs}"
        if self.drel is not None:
            repr += f" drel={self.drel}"
        if self.curvat is not None:
            repr += f" curvat={self.curvat}"
        return repr