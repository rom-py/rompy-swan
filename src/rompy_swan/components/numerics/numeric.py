"""SWAN NUMERIC component."""

from typing import Literal, Optional, Union

from pydantic import Field

from rompy_swan.components.base import BaseComponent
from rompy_swan.components.numerics.options import (
    ACCUR,
    CTHETA,
    CSIGMA,
    DIRIMPL,
    SETUP,
    SIGIMPL,
    STOPC,
)


class NUMERIC(BaseComponent):
    """Numerical properties.

    .. code-block:: text

        NUMeric ( STOPC [dabs] [drel] [curvat] [npnts] ->STAT|NONSTAT [limiter] ) &
            ( DIRimpl [cdd] ) ( SIGIMpl [css] [eps2] [outp] [niter] ) &
            ( CTheta [cfl] ) ( CSigma [cfl] ) ( SETUP [eps2] [outp] [niter] )

    Examples
    --------
    .. ipython:: python
        :okwarning:

        from rompy_swan.components.numerics.numeric import NUMERIC
        numeric = NUMERIC()
        print(numeric.render())
        numeric = NUMERIC(
            stop=dict(
                model_type="stopc",
                dabs=0.05,
                drel=0.01,
                curvat=0.05,
                npnts=99.5,
            ),
            dirimpl=dict(cdd=0.5),
            sigimpl=dict(css=0.5, eps2=1e-4, outp=0, niter=20),
            ctheta=dict(cfl=0.9),
            csigma=dict(cfl=0.9),
            setup=dict(eps2=1e-4, outp=0, niter=20),
        )
        print(numeric.render())

    """

    model_type: Literal["numeric", "NUMERIC"] = Field(
        default="numeric", description="Model type discriminator"
    )
    stop: Optional[Union[STOPC, ACCUR]] = Field(
        default=None,
        description="Iteration termination criteria",
        discriminator="model_type",
    )
    dirimpl: Optional[DIRIMPL] = Field(
        default=None,
        description="Numerical scheme for refraction",
    )
    sigimpl: Optional[SIGIMPL] = Field(
        default=None,
        description="Frequency shifting accuracy",
    )
    ctheta: Optional[CTHETA] = Field(
        default=None,
        description="Prevents excessive directional turning",
    )
    csigma: Optional[CSIGMA] = Field(
        default=None,
        description="Prevents excessive frequency shifting",
    )
    setup: Optional[SETUP] = Field(
        default=None,
        description="Stop criteria in the computation of wave setup",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "NUMERIC"
        if self.stop is not None:
            repr += f" {self.stop.render()}"
        if self.dirimpl is not None:
            repr += f" {self.dirimpl.render()}"
        if self.sigimpl is not None:
            repr += f" {self.sigimpl.render()}"
        if self.ctheta is not None:
            repr += f" {self.ctheta.render()}"
        return repr
