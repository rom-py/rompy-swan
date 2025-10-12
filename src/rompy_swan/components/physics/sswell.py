"""SWAN swell dissipation components.

This module contains components for configuring swell dissipation in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class NEGATINP(BaseComponent):
    """Negative wind input.

    .. code-block:: text

        NEGATINP [rdcoef]

    With this optional command the user activates negative wind input. **This is
    intended only for use with non-breaking swell dissipation SSWELL ZIEGER**.
    Parameter `rdcoef` is a fraction between 0 and 1, representing the strength of
    negative wind input. As an example, with [rdcoef]=0.04, for a spectral bin that is
    opposed to the wind direction, the wind input factor W(k, θ) is negative, and its
    magnitude is 4% of the corresponding value of the spectral bin that is in the
    opposite direction (i.e. in the wind direction). See Zieger et al. (2015) eq. 11,
    where a0 is their notation for [rdcoef]. Default [rdcoef]=0.0 and `rdcoef=0.04` is
    recommended, though as implied by Zieger et al. (2015), this value is not
    well-established, so the user is encouraged to experiment with other values.

    References
    ----------
    Zieger, S., Babanin, A.V., Rogers, W.E. and Young, I.R., 2015. Observation-based
    source terms in the third-generation wave model WAVEWATCH. Ocean Modelling, 96,
    pp.2-25.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import NEGATINP
        negatinp = NEGATINP()
        print(negatinp.render())
        negatinp = NEGATINP(rdcoef=0.04)
        print(negatinp.render())

    """

    model_type: Literal["negatinp", "NEGATINP"] = Field(
        default="negatinp", description="Model type discriminator"
    )
    rdcoef: Optional[float] = Field(
        default=None,
        description="Coefficient representing the strength of negative wind input",
        ge=0.0,
        le=1.0,
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "NEGATINP"
        if self.rdcoef is not None:
            repr += f" rdcoef={self.rdcoef}"
        return repr


class SSWELL_ROGERS(BaseComponent):
    """Nonbreaking dissipation of Rogers et al. (2012).

    .. code-block:: text

        SSWELL ROGERS [cdsv] [feswell]

    References
    ----------
    Rogers, W.E., Babanin, A.V. and Wang, D.W., 2012. Observation-consistent input and
    whitecapping dissipation in a model for wind-generated surface waves: Description
    and simple calculations. Journal of Atmospheric and Oceanic Technology, 29(9),
    pp.1329-1346.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import SSWELL_ROGERS
        sswell = SSWELL_ROGERS()
        print(sswell.render())
        sswell = SSWELL_ROGERS(cdsv=1.2, feswell=0.5)
        print(sswell.render())

    """

    model_type: Literal["rogers", "ROGERS"] = Field(
        default="rogers", description="Model type discriminator"
    )
    cdsv: Optional[float] = Field(
        default=None,
        description=(
            "Coefficient related to laminar atmospheric boundary layer "
            "(SWAN default: 1.2)"
        ),
    )
    feswell: Optional[float] = Field(
        default=None, description="Swell dissipation factor"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "SSWELL ROGERS"
        if self.cdsv is not None:
            repr += f" cdsv={self.cdsv}"
        if self.feswell is not None:
            repr += f" feswell={self.feswell}"
        return repr


class SSWELL_ARDHUIN(BaseComponent):
    """Nonbreaking dissipation of Ardhuin et al. (2010).

    .. code-block:: text

        SSWELL ARDHUIN [cdsv]

    References
    ----------
    Ardhuin, F., Rogers, E., Babanin, A.V., Filipot, J.F., Magne, R., Roland, A.,
    Van Der Westhuysen, A., Queffeulou, P., Lefevre, J.M., Aouf, L. and Collard, F.,
    2010. Semiempirical dissipation source functions for ocean waves. Part I:
    Definition, calibration, and validation. Journal of Physical Oceanography, 40(9),
    pp.1917-1941.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import SSWELL_ARDHUIN
        sswell = SSWELL_ARDHUIN()
        print(sswell.render())
        sswell = SSWELL_ARDHUIN(cdsv=1.2)
        print(sswell.render())

    """

    model_type: Literal["ardhuin", "ARDHUIN"] = Field(
        default="ardhuin", description="Model type discriminator"
    )
    cdsv: Optional[float] = Field(
        default=None,
        description=(
            "Coefficient related to laminar atmospheric boundary layer "
            "(SWAN default: 1.2)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "SSWELL ARDHUIN"
        if self.cdsv is not None:
            repr += f" cdsv={self.cdsv}"
        return repr


class SSWELL_ZIEGER(BaseComponent):
    """Nonbreaking dissipation of Zieger et al. (2015).

    .. code-block:: text

        SSWELL ZIEGER [b1]

    Swell dissipation of Young et al. (2013) updated by Zieger et al. (2015). The
    Zieger option is intended for use with negative wind input via the NEGATINP
    command. Zieger non-breaking dissipation follows the method used in WAVEWATCH III
    version 4 and does not include the steepness-dependent swell coefficient introduced
    in WAVEWATCH III version 5.

    References
    ----------
    Zieger, S., Babanin, A.V., Rogers, W.E. and Young, I.R., 2015. Observation-based
    source terms in the third-generation wave model WAVEWATCH. Ocean Modelling, 96,
    pp.2-25.

    Young, I.R., Babanin, A.V. and Zieger, S., 2013. The decay rate of ocean swell
    observed by altimeter. Journal of physical oceanography, 43(11), pp.2322-2333.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import SSWELL_ZIEGER
        sswell = SSWELL_ZIEGER()
        print(sswell.render())
        sswell = SSWELL_ZIEGER(b1=0.00025)
        print(sswell.render())

    """

    model_type: Literal["zieger", "ZIEGER"] = Field(
        default="zieger", description="Model type discriminator"
    )
    b1: Optional[float] = Field(
        default=None,
        description="Non-dimensional proportionality coefficient "
        "(SWAN default: 0.00025)",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "SSWELL ZIEGER"
        if self.b1 is not None:
            repr += f" b1={self.b1}"
        return repr
