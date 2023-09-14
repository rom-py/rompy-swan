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
