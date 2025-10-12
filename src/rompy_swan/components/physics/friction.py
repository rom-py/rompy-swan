"""SWAN bottom friction components.

This module contains components for configuring bottom friction in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class FRICTION_JONSWAP(BaseComponent):
    """Hasselmann et al. (1973) Jonswap friction.

    .. code-block:: text

        FRICTION JONSWAP CONSTANT [cfjon]

    Indicates that the semi-empirical expression derived from the JONSWAP results for
    bottom friction dissipation (Hasselmann et al., 1973, JONSWAP) should be activated.
    This option is default.

    References
    ----------
    Hasselmann, K., Barnett, T.P., Bouws, E., Carlson, H., Cartwright, D.E., Enke, K.,
    Ewing, J.A., Gienapp, A., Hasselmann, D.E., Kruseman, P. and Meerburg, A., 1973.
    Measurements of wind-wave growth and swell decay during the Joint North Sea Wave
    Project (JONSWAP). Deutches Hydrographisches Institut, Hamburg, Germany,
    Rep. No. 12, 95 pp.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import FRICTION_JONSWAP
        friction = FRICTION_JONSWAP()
        print(friction.render())
        friction = FRICTION_JONSWAP(cfjon=0.038)
        print(friction.render())

    TODO: Implement VARIABLE option?

    """

    model_type: Literal["jonswap", "JONSWAP"] = Field(
        default="jonswap", description="Model type discriminator"
    )
    cfjon: Optional[float] = Field(
        default=None,
        description="Coefficient of the JONSWAP formulation (SWAN default: 0.038)",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "FRICTION JONSWAP CONSTANT"
        if self.cfjon is not None:
            repr += f" cfjon={self.cfjon}"
        return repr


class FRICTION_COLLINS(BaseComponent):
    """Collins (1972) friction.

    .. code-block:: text

        FRICTION COLLINS [cfw]

    Note that `cfw` is allowed to vary over the computational region; in that case use
    the commands INPGRID FRICTION and READINP FRICTION to define and read the friction
    data. This command FRICTION is still required to define the type of friction
    expression. The value of `cfw` in this command is then not required (it will be
    ignored).

    References
    ----------
    Collins, J.I., 1972. Prediction of shallow-water spectra. Journal of Geophysical
    Research, 77(15), pp.2693-2707.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import FRICTION_COLLINS
        friction = FRICTION_COLLINS()
        print(friction.render())
        friction = FRICTION_COLLINS(cfw=0.038)
        print(friction.render())

    """

    model_type: Literal["collins", "COLLINS"] = Field(
        default="collins", description="Model type discriminator"
    )
    cfw: Optional[float] = Field(
        default=None,
        description="Collins bottom friction coefficient (SWAN default: 0.015)",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "FRICTION COLLINS"
        if self.cfw is not None:
            repr += f" cfw={self.cfw}"
        return repr


class FRICTION_MADSEN(BaseComponent):
    """Madsen et al (1988) friction.

    .. code-block:: text

        FRICTION MADSEN [kn]

    Note that `kn` is allowed to vary over the computational region; in that case use
    the commands INPGRID FRICTION and READINP FRICTION to define and read the friction
    data. This command FRICTION is still required to define the type of friction
    expression. The value of `kn` in this command is then not required (it will be
    ignored).

    References
    ----------
    Madsen, O.S., Poon, Y.K. and Graber, H.C., 1988. Spectral wave attenuation by
    bottom friction: Theory. In Coastal engineering 1988 (pp. 492-504).

    Madsen, O.S. and Rosengaus, M.M., 1988. Spectral wave attenuation by bottom
    friction: Experiments. In Coastal Engineering 1988 (pp. 849-857).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import FRICTION_MADSEN
        friction = FRICTION_MADSEN()
        print(friction.render())
        friction = FRICTION_MADSEN(kn=0.038)
        print(friction.render())

    """

    model_type: Literal["madsen", "MADSEN"] = Field(
        default="madsen", description="Model type discriminator"
    )
    kn: Optional[float] = Field(
        default=None,
        description=(
            "equivalent roughness length scale of the bottom (in m) "
            "(SWAN default: 0.05)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "FRICTION MADSEN"
        if self.kn is not None:
            repr += f" kn={self.kn}"
        return repr


class FRICTION_RIPPLES(BaseComponent):
    """Smith et al. (2011) Ripples friction.

    .. code-block:: text

        FRICTION RIPPLES [S] [D]

    Indicates that the expression of Smith et al. (2011) should be activated. Here
    friction depends on the formation of bottom ripples and sediment size.

    References
    ----------
    Smith, G.A., Babanin, A.V., Riedel, P., Young, I.R., Oliver, S. and Hubbert, G.,
    2011. Introduction of a new friction routine into the SWAN model that evaluates
    roughness due to bedform and sediment size changes. Coastal Engineering, 58(4),
    pp.317-326.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import FRICTION_RIPPLES
        friction = FRICTION_RIPPLES()
        print(friction.render())
        friction = FRICTION_RIPPLES(s=2.65, d=0.0001)
        print(friction.render())

    """

    model_type: Literal["ripples", "RIPPLES"] = Field(
        default="ripples", description="Model type discriminator"
    )
    s: Optional[float] = Field(
        default=None,
        description="The specific gravity of the sediment (SWAN default: 2.65)",
    )
    d: Optional[float] = Field(
        default=None, description="The sediment diameter (in m) (SWAN default: 0.0001)"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "FRICTION RIPPLES"
        if self.s is not None:
            repr += f" S={self.s}"
        if self.d is not None:
            repr += f" D={self.d}"
        return repr
