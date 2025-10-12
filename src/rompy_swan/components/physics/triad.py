"""SWAN triad interaction components.

This module contains components for configuring triad wave-wave interactions in SWAN.
"""

from typing import Literal, Optional, Union

from pydantic import Field

from rompy_swan.components.base import BaseComponent
from rompy_swan.components.physics.options.biphase import DEWIT, ELDEBERKY


class TRIAD(BaseComponent):
    """Wave triad interactions.

    .. code-block:: text

        TRIAD [itriad] [trfac] [cutfr] [a] [b] [urcrit] [urslim]

    With this command the user can activate the triad wave-wave interactions. If this
    command is not used, SWAN will not account for triads.

    Note
    ----
    This is the TRIAD specification in SWAN < 41.45.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import TRIAD
        triad = TRIAD()
        print(triad.render())
        triad = TRIAD(
            itriad=1,
            trfac=0.8,
            cutfr=2.5,
            a=0.95,
            b=-0.75,
            ucrit=0.2,
            urslim=0.01,
        )
        print(triad.render())

    """

    model_type: Literal["triad", "TRIAD"] = Field(
        default="triad", description="Model type discriminator"
    )
    itriad: Optional[Literal[1, 2]] = Field(
        default=None,
        description=(
            "Approximation method for the triad computation: \n\n* 1: the LTA method "
            "of Eldeberky (1996) \n* 2: the SPB method of Becq-Girard et al. (1999) "
            "(SWAN default: 1)"
        ),
    )
    trfac: Optional[float] = Field(
        default=None,
        description=(
            "Proportionality coefficient (SWAN default: 0.8 in case of LTA method, "
            "0.9 in case of SPB method)"
        ),
    )
    cutfr: Optional[float] = Field(
        default=None,
        description=(
            "Controls the maximum frequency that is considered in the LTA "
            "computation. The value of `cutfr` is the ratio of this maximum "
            "frequency over the mean frequency (SWAN default: 2.5)"
        ),
    )
    a: Optional[float] = Field(
        default=None,
        description=(
            "First calibration parameter for tuning K in Eq. (5.1) of Becq-Girard et "
            "al. (1999). This parameter is associated with broadening of the "
            "resonance condition (SWAN default: 0.95)"
        ),
    )
    b: Optional[float] = Field(
        default=None,
        description=(
            "Second calibration parameter for tuning K in Eq. (5.1) of Becq-Girard "
            "et al. (1999). This parameter is associated with broadening of the "
            "resonance condition (SWAN default: -0.75 for 1D, 0.0 for 2D"
        ),
    )
    ucrit: Optional[float] = Field(
        default=None,
        description=(
            "The critical Ursell number appearing in the expression for the biphase "
            "(SWAN default: 0.2)"
        ),
    )
    urslim: Optional[float] = Field(
        default=None,
        description=(
            "The lower threshold for Ursell number, if the actual Ursell number is "
            "below this value triad interactions are be computed (SWAN default: 0.01)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "TRIAD"
        if self.itriad is not None:
            repr += f" itriad={self.itriad}"
        if self.trfac is not None:
            repr += f" trfac={self.trfac}"
        if self.cutfr is not None:
            repr += f" cutfr={self.cutfr}"
        if self.a is not None:
            repr += f" a={self.a}"
        if self.b is not None:
            repr += f" b={self.b}"
        if self.ucrit is not None:
            repr += f" urcrit={self.ucrit}"
        if self.urslim is not None:
            repr += f" urslim={self.urslim}"
        return repr


class DCTA(BaseComponent):
    """Triad interactions with the DCTA method of Booij et al. (2009).

    .. code-block:: text

        TRIAD DCTA [trfac] [p] COLL|NONC BIPHHASE ELDEBERKY|DEWIT

    References
    ----------
    Booij, N., Holthuijsen, L.H. and Bénit, M.P., 2009. A distributed collinear triad
    approximation in SWAN. In Proceedings Of Coastal Dynamics 2009: Impacts of Human
    Activities on Dynamic Coastal Processes (With CD-ROM) (pp. 1-10).

    Note
    ----
    This is the default method to compute the triad interactions in SWAN >= 41.45, it
    is not supported in earlier versions of the model.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics.triad import DCTA
        triad = DCTA()
        print(triad.render())
        triad = DCTA(
            trfac=4.4,
            p=1.3,
            noncolinear=True,
            biphase={"model_type": "dewit", "lpar": 0.0},
        )
        print(triad.render())

    """

    model_type: Literal["dcta", "DCTA"] = Field(
        default="dcta", description="Model type discriminator"
    )
    trfac: Optional[float] = Field(
        default=None,
        description=(
            "Scaling factor that controls the intensity of "
            "the triad interaction due to DCTA (SWAN default: 4.4)"
        ),
    )
    p: Optional[float] = Field(
        default=None,
        description=(
            "Shape coefficient to force the high-frequency tail(SWAN default: 4/3)"
        ),
    )
    noncolinear: bool = Field(
        default=False,
        description=(
            "If True, the noncolinear triad interactions "
            "with the DCTA framework are accounted for"
        ),
    )
    biphase: Optional[Union[ELDEBERKY, DEWIT]] = Field(
        default=None,
        description=(
            "Defines the parameterization of biphase (self-self interaction) "
            "(SWAN default: ELDEBERKY)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "TRIAD DCTA"
        if self.trfac is not None:
            repr += f" trfac={self.trfac}"
        if self.p is not None:
            repr += f" p={self.p}"
        if self.noncolinear:
            repr += " NONC"
        else:
            repr += " COLL"
        if self.biphase is not None:
            repr += f" {self.biphase.render()}"
        return repr


class LTA(BaseComponent):
    """Triad interactions with the LTA method of Eldeberky (1996).

    .. code-block:: text

        TRIAD LTA [trfac] [cutfr] BIPHHASE ELDEBERKY|DEWIT

    References
    ----------
    Eldeberky, Y., Polnikov, V. and Battjes, J.A., 1996. A statistical approach for
    modeling triad interactions in dispersive waves. In Coastal Engineering 1996
    (pp. 1088-1101).

    Note
    ----
    This method to compute the triad interactions is only supported in SWAN >= 41.45.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics.triad import LTA
        triad = LTA()
        print(triad.render())
        triad = LTA(
            trfac=0.8,
            cutfr=2.5,
            biphase={"model_type": "eldeberky", "urcrit": 0.63},
        )
        print(triad.render())

    """

    model_type: Literal["lta", "LTA"] = Field(
        default="lta", description="Model type discriminator"
    )
    trfac: Optional[float] = Field(
        default=None,
        description=(
            "Scaling factor that controls the intensity of "
            "the triad interaction due to LTA (SWAN default: 0.8)"
        ),
    )
    cutfr: Optional[float] = Field(
        default=None,
        description=(
            "Controls the maximum frequency that is considered in the LTA "
            "computation. The value of `cutfr` is the ratio of this maximum "
            "frequency over the mean frequency (SWAN default: 2.5)"
        ),
    )
    biphase: Optional[Union[ELDEBERKY, DEWIT]] = Field(
        default=None,
        description=(
            "Defines the parameterization of biphase (self-self interaction) "
            "(SWAN default: ELDEBERKY)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "TRIAD LTA"
        if self.trfac is not None:
            repr += f" trfac={self.trfac}"
        if self.cutfr is not None:
            repr += f" cutfr={self.cutfr}"
        if self.biphase is not None:
            repr += f" {self.biphase.render()}"
        return repr


class SPB(BaseComponent):
    """Triad interactions with the SPB method of Becq-Girard et al. (1999).

    .. code-block:: text

        TRIAD SPB [trfac] [a] [b] BIPHHASE ELDEBERKY|DEWIT

    References
    ----------
    Becq-Girard, F., Forget, P. and Benoit, M., 1999. Non-linear propagation of
    unidirectional wave fields over varying topography. Coastal Engineering, 38(2),
    pp.91-113.

    Note
    ----
    This method to compute the triad interactions is only supported in SWAN >= 41.45.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics.triad import SPB
        triad = SPB()
        print(triad.render())
        triad = SPB(
            trfac=0.9,
            a=0.95,
            b=0.0,
            biphase={"model_type": "eldeberky", "urcrit": 0.63},
        )
        print(triad.render())

    """

    model_type: Literal["spb", "SPB"] = Field(
        default="spb", description="Model type discriminator"
    )
    trfac: Optional[float] = Field(
        default=None,
        description=(
            "Scaling factor that controls the intensity of "
            "the triad interaction due to SPB (SWAN default: 0.9)"
        ),
    )
    a: Optional[float] = Field(
        default=None,
        description=(
            "First calibration parameter for tuning K in Eq. (5.1) of "
            "Becq-Girard et al. (1999). This parameter is associated with broadening "
            "of the resonance condition. The default value is 0.95 and is calibrated "
            "by means of laboratory experiments (SWAN default: 0.95)"
        ),
    )
    b: Optional[float] = Field(
        default=None,
        description=(
            "Second calibration parameter for tuning K in Eq. (5.1) of "
            "Becq-Girard et al. (1999). This parameter is associated with broadening "
            "of the resonance condition. The default value is -0.75 and is calibrated "
            "by means of laboratory experiments. However, it may not be appropriate "
            "for true 2D field cases as it does not scale with the wave field "
            "characteristics. Hence, this parameter is set to zero (SWAN default: 0.0)"
        ),
    )
    biphase: Optional[Union[ELDEBERKY, DEWIT]] = Field(
        default=None,
        description=(
            "Defines the parameterization of biphase (self-self interaction) "
            "(SWAN default: ELDEBERKY)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "TRIAD SPB"
        if self.trfac is not None:
            repr += f" trfac={self.trfac}"
        if self.a is not None:
            repr += f" a={self.a}"
        if self.b is not None:
            repr += f" b={self.b}"
        if self.biphase is not None:
            repr += f" {self.biphase.render()}"
        return repr
