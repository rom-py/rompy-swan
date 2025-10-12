"""SWAN scattering component.

This module contains the SCAT component for wave scattering in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field, model_validator

from rompy.logging import get_logger
from rompy_swan.components.base import BaseComponent

logger = get_logger(__name__)


class SCAT(BaseComponent):
    """Scattering.

    .. code-block:: text

        SCAT [iqcm] (GRID [rfac]) (TRUNC [alpha] [qmax])

    Using this optional command, the user activates a source term that allows for the
    generation and propagation of cross correlations between scattered waves due to
    variations in the bathymetry and mean currents. Such variations are rapid compared
    to the distancebetween the crossing waves (at the scale of 100-1000 m) and is
    particularly relevant for cases involving narrowband waves (swells) in coastal
    regions with shallow water and ambient currents. In turn, the immediate spatial
    effects of coherent scattering, interference, refraction and diffraction can cause
    large-scale changes in the wave parameters.

    References
    ----------
    Smit, P.B. and Janssen, T.T., 2013. The evolution of inhomogeneous wave statistics
    through a variable medium. Journal of Physical Oceanography, 43(8), pp.1741-1758.

    Smit, P.B., Janssen, T.T. and Herbers, T.H.C., 2015. Stochastic modeling of
    inhomogeneous ocean waves. Ocean Modelling, 96, pp.26-35.

    Smit, P.B., Janssen, T.T. and Herbers, T.H.C., 2015. Stochastic modeling of
    coherent wave fields over variable depth. Journal of Physical Oceanography, 45(4),
    pp.1139-1154.

    Akrish, G., Smit, P., Zijlema, M. and Reniers, A., 2020. Modelling statistical wave
    interferences over shear currents. Journal of Fluid Mechanics, 891, p.A2.

    Notes
    -----
    Implemented in SWAN 41.41.

    If both `alpha` and `qmax` options are provided to truncate the infinite
    convolution sum their mimimum is considered as the final limit on the sum.

    Examples
    --------

    .. ipython:: python

        from rompy_swan.components.physics import SCAT
        scat = SCAT()
        print(scat.render())
        scat = SCAT(iqcm=2, rfac=1.0, alpha=1.0)
        print(scat.render())

    """

    model_type: Literal["scat", "SCAT"] = Field(
        default="scat", description="Model type discriminator"
    )
    iqcm: Optional[Literal[0, 1, 2]] = Field(
        default=None,
        description=(
            "Indicates the modelling and computation of QC scattering:\n\n* 0: no "
            "scattering\n* 1: scattering due to non-uniform bathymetry and currents "
            "(the latter only if applicable; see command `INPGRID CURRENT`)\n* 2: "
            "wave-current interaction under the assumption of a slowly varying "
            "bathymetry\n\n(SWAN default: 1)"
        ),
    )
    rfac: Optional[float] = Field(
        default=None,
        description=(
            "The resolution factor through which the incident spectral width is"
            "multiplied (SWAN default: 1.0)"
        ),
        ge=1.0,
    )
    alpha: Optional[float] = Field(
        default=None,
        description=(
            "The coefficient by which the mean wave number is multiplied to set the"
            "limit on the convolution sum (SWAN default: 1.0)"
        ),
    )
    qmax: Optional[float] = Field(
        default=None, description="The maximum scattering wave number (in 1/m)"
    )

    @model_validator(mode="after")
    def warn_if_qmax_and_alpha(self) -> "SCAT":
        if self.qmax is not None and self.alpha is not None:
            logger.warning(
                "Both `alpha` and `qmax` options are provided to truncate the "
                "infinite convolution sum. Their mimimum is considered in SWAN as the "
                "final limit on the sum"
            )
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "SCAT"
        if self.iqcm is not None:
            repr += f" iqcm={self.iqcm}"
        if self.rfac is not None:
            repr += f" GRID rfac={self.rfac}"
        if self.alpha is not None or self.qmax is not None:
            repr += " TRUNC"
            if self.alpha is not None:
                repr += f" alpha={self.alpha}"
            if self.qmax is not None:
                repr += f" qmax={self.qmax}"
        return repr
