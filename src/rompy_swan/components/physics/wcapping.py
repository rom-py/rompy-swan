"""SWAN whitecapping components.

This module contains components for configuring whitecapping dissipation in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class WCAPPING_KOMEN(BaseComponent):
    """Whitecapping according to Komen (1984).

    .. code-block:: text

        WCAPPING KOMEN [cds2] [stpm] [powst] [delta] [powk]

    Notes
    -----
    The SWAN default for `delta` has been changed since version 40.91A. The setting
    `delta = 1` will improve the prediction of the wave energy at low frequencies, and
    hence the mean wave period. The original default was `delta = 0`, which corresponds
    to WAM Cycle 3. See the Scientific/Technical documentation for further details.

    References
    ----------
    Komen, G.J., Hasselmann, S. and Hasselmann, K., 1984. On the existence of a fully
    developed wind-sea spectrum. Journal of physical oceanography, 14(8), pp.1271-1285.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import WCAPPING_KOMEN
        wcapping = WCAPPING_KOMEN()
        print(wcapping.render())
        wcapping = WCAPPING_KOMEN(cds2=2.36e-5, stpm=3.02e-3, powst=2, delta=1, powk=2)
        print(wcapping.render())

    """

    model_type: Literal["komen", "KOMEN"] = Field(
        default="komen", description="Model type discriminator"
    )
    cds2: Optional[float] = Field(
        default=None,
        description=(
            "Coefficient for determining the rate of whitecapping dissipation ($Cds$) "
            "(SWAN default: 2.36e-5)"
        ),
    )
    stpm: Optional[float] = Field(
        default=None,
        description=(
            "Value of the wave steepness for a Pierson-Moskowitz spectrum "
            "($s^2_{PM}$) (SWAN default: 3.02e-3)"
        ),
    )
    powst: Optional[float] = Field(
        default=None,
        description=(
            "Power of steepness normalized with the wave steepness "
            "of a Pierson-Moskowitz spectrum (SWAN default: 2)"
        ),
    )
    delta: Optional[float] = Field(
        default=None,
        description=(
            "Coefficient which determines the dependency of the whitecapping "
            "on wave number (SWAN default: 1)"
        ),
    )
    powk: Optional[float] = Field(
        default=None,
        description=(
            "power of wave number normalized with the mean wave number "
            "(SWAN default: 1)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "WCAPPING KOMEN"
        if self.cds2 is not None:
            repr += f" cds2={self.cds2}"
        if self.stpm is not None:
            repr += f" stpm={self.stpm}"
        if self.powst is not None:
            repr += f" powst={self.powst}"
        if self.delta is not None:
            repr += f" delta={self.delta}"
        if self.powk is not None:
            repr += f" powk={self.powk}"
        return repr


class WCAPPING_AB(BaseComponent):
    """Whitecapping according to Alves and Banner (2003).

    .. code-block:: text

        WCAPPING AB [cds2] [br] CURRENT [cds3]

    References
    ----------
    Alves, J.H.G. and Banner, M.L., 2003. Performance of a saturation-based
    dissipation-rate source term in modeling the fetch-limited evolution of wind waves.
    Journal of Physical Oceanography, 33(6), pp.1274-1298.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import WCAPPING_AB
        wcapping = WCAPPING_AB()
        print(wcapping.render())
        wcapping = WCAPPING_AB(cds2=5.0e-5, br=1.75e-3, current=True, cds3=0.8)
        print(wcapping.render())

    """

    model_type: Literal["ab", "AB"] = Field(
        default="ab", description="Model type discriminator"
    )
    cds2: Optional[float] = Field(
        default=None,
        description=(
            "proportionality coefficient due to Alves and Banner (2003) "
            "(SWAN default: 5.0e-5)"
        ),
    )
    br: Optional[float] = Field(
        default=None, description="Threshold saturation level	(SWAN default: 1.75e-3)"
    )
    current: bool = Field(
        default=False,
        description=(
            "Indicates that enhanced current-induced dissipation "
            "as proposed by Van der Westhuysen (2012) is to be added"
        ),
    )
    cds3: Optional[float] = Field(
        default=None, description="Proportionality coefficient (SWAN default: 0.8)"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "WCAPPING AB"
        if self.cds2 is not None:
            repr += f" cds2={self.cds2}"
        if self.br is not None:
            repr += f" br={self.br}"
        if self.current:
            repr += " CURRENT"
        if self.cds3 is not None:
            repr += f" cds3={self.cds3}"
        return repr
