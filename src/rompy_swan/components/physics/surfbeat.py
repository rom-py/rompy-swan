"""SWAN surfbeat component.

This module contains the SURFBEAT component for infragravity energy in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class SURFBEAT(BaseComponent):
    """Surfbeat.

    .. code-block:: text

        SURFBEAT [df] [nmax] [emin] UNIFORM/LOGARITHMIC

    Using this optional command, the user activates the Infragravity Energy Module
    (IEM) of Reniers and Zijlema (2022). Besides the energy balance equation for a
    sea-swell wave field, another energy balance is included to account for the
    transfer of sea-swell energy to the bound infragravity (BIG) wave. This
    infragravity energy balance also involves a nonlinear transfer, expressed by the
    biphase, through the phase coupling between the radiation stress forcing and the
    BIG wave. For the prediction of the biphase for obliquely incident waves, an
    evolution equation is provided under the assumption that the bottom slopes are mild
    and alongshore uniform.

    References
    ----------
    Reniers, A. and Zijlema, M., 2022. Swan surfbeat-1d. Coastal Engineering, 172,
    p.104068.

    Examples
    --------

    .. ipython:: python

        from rompy_swan.components.physics import SURFBEAT
        surfbeat = SURFBEAT()
        print(surfbeat.render())
        surfbeat = SURFBEAT(df=0.01, nmax=50000, emin=0.05, spacing="logarithmic")
        print(surfbeat.render())

    """

    model_type: Literal["surfbeat", "SURFBEAT"] = Field(
        default="surfbeat", description="Model type discriminator"
    )
    df: Optional[float] = Field(
        default=None,
        description=(
            "The constant size of BIG frequency bin (in Hz) (SWAN default: 0.01)"
        ),
        ge=0.0,
    )
    nmax: Optional[int] = Field(
        default=None,
        description=(
            "The maximum number of short-wave pairs for creating bichromatic wave "
            "groups (SWAN default: 50000)"
        ),
        ge=0,
    )
    emin: Optional[float] = Field(
        default=None,
        description=(
            "The energy threshold in fraction of energy spectrum peak. With this "
            "threshold one takes into account those short wave components to create "
            "bichromatic wave groups while their energy levels are larger than "
            "`emin x E_max` with `E_max` the peak of the spectrum (SWAN default: 0.05)"
        ),
    )
    spacing: Optional[Literal["uniform", "logarithmic"]] = Field(
        default=None,
        description=(
            "Define if frequencies for reflected ig waves are uniformly or "
            "logarithmically distributed"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "SURFBEAT"
        if self.df is not None:
            repr += f" df={self.df}"
        if self.nmax is not None:
            repr += f" nmax={self.nmax}"
        if self.emin is not None:
            repr += f" emin={self.emin}"
        if self.spacing is not None:
            repr += f" {self.spacing.upper()}"
        return repr
