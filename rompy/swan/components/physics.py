"""Model physics components."""
import logging
from typing import Literal, Optional, Union, Annotated
from pydantic import validator, root_validator, Field, confloat

from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.physics import (
    JANSSEN,
    KOMEN,
    WESTHUYSEN,
    ST6,
    ST6C1,
    ST6C2,
    ST6C3,
    ST6C4,
    ST6C5,
    ELDEBERKY,
    DEWIT,
)


logger = logging.getLogger(__name__)


SOURCE_TERMS = Union[
    JANSSEN,
    KOMEN,
    WESTHUYSEN,
    ST6,
    ST6C1,
    ST6C2,
    ST6C3,
    ST6C4,
    ST6C5,
]


# =====================================================================================
# Wave generation GEN1 | GEN2 | GEN3
# =====================================================================================
class GEN1(BaseComponent):
    """First generation source terms GEN1.

    `GEN1 [cf10] [cf20] [cf30] [cf40] [edmlpm] [cdrag] [umin] [cfpm]`

    With this command the user indicates that SWAN should run in first-generation mode
    (see Scientific/Technical documentation).

    """

    model_type: Literal["gen1"] = Field(
        default="gen1", description="Model type discriminator"
    )
    cf10: Optional[float] = Field(
        description="Controls the linear wave growth (SWAN default: 188.0)"
    )
    cf20: Optional[float] = Field(
        description="Controls the exponential wave growth (SWAN default: 0.59)"
    )
    cf30: Optional[float] = Field(
        description="Controls the exponential wave growth (SWAN default: 0.12)"
    )
    cf40: Optional[float] = Field(
        description=(
            "Controls the dissipation rate, i.e., the time decay scale "
            "(SWAN default: 250.0)"
        )
    )
    edmlpm: Optional[float] = Field(
        description=(
            "Maximum non-dimensionless energy density of the wind sea part of the "
            "spectrum according to Pierson Moskowitz (SWAN default: 0.0036)"
        )
    )
    cdrag: Optional[float] = Field(
        description="Drag coefficient (SWAN default: 0.0012)"
    )
    umin: Optional[float] = Field(
        description=(
            "Minimum wind velocity (relative to current; all wind speeds "
            "are taken at 10 m above sea level) (SWAN default: 1)"
        )
    )
    cfpm: Optional[float] = Field(
        description=(
            "Coefficient which determines the Pierson Moskowitz frequency: "
            "`delta_PM = 2pi g / U_10` (SWAN default: 0.13)"
        )
    )

    def cmd(self):
        repr = "GEN1"
        if self.cf10 is not None:
            repr += f" cf10={self.cf10}"
        if self.cf20 is not None:
            repr += f" cf20={self.cf20}"
        if self.cf30 is not None:
            repr += f" cf30={self.cf30}"
        if self.cf40 is not None:
            repr += f" cf40={self.cf40}"
        if self.edmlpm is not None:
            repr += f" edmlpm={self.edmlpm}"
        if self.cdrag is not None:
            repr += f" cdrag={self.cdrag}"
        if self.umin is not None:
            repr += f" umin={self.umin}"
        if self.cfpm is not None:
            repr += f" cfpm={self.cfpm}"
        return repr


class GEN2(GEN1):
    """Second generation source terms GEN2.

    `GEN2 [cf10] [cf20] [cf30] [cf40] [cf50] [cf60] [edmlpm] [cdrag] [umin] [cfpm]`

    With this command the user indicates that SWAN should run in second-generation mode
    (see Scientific/Technical documentation).

    """

    model_type: Literal["gen2"] = Field(
        default="gen2", description="Model type discriminator"
    )
    cf50: Optional[float] = Field(
        description=(
            "Controls the spectral energy scale of the limit spectrum "
            "(SWAN default: 0.0023)"
        )
    )
    cf60: Optional[float] = Field(
        description=(
            "Ccontrols the spectral energy scale of the limit spectrum "
            "(SWAN default: -0.223"
        )
    )

    def cmd(self):
        repr = "GEN2"
        if self.cf10 is not None:
            repr += f" cf10={self.cf10}"
        if self.cf20 is not None:
            repr += f" cf20={self.cf20}"
        if self.cf30 is not None:
            repr += f" cf30={self.cf30}"
        if self.cf40 is not None:
            repr += f" cf40={self.cf40}"
        if self.cf50 is not None:
            repr += f" cf50={self.cf50}"
        if self.cf60 is not None:
            repr += f" cf60={self.cf60}"
        if self.edmlpm is not None:
            repr += f" edmlpm={self.edmlpm}"
        if self.cdrag is not None:
            repr += f" cdrag={self.cdrag}"
        if self.umin is not None:
            repr += f" umin={self.umin}"
        if self.cfpm is not None:
            repr += f" cfpm={self.cfpm}"
        return repr


class GEN3(BaseComponent):
    """Third generation source terms GEN3.

    `GEN3 JANSSEN|KOMEN|WESTHUYSEN|ST6 (...) AGROW [a]`

    With this command the user indicates that SWAN should run in third-generation mode
    for wind input, quadruplet interactions and whitecapping.

    """

    model_type: Literal["gen3"] = Field(
        default="gen3", description="Model type discriminator"
    )
    source_terms: SOURCE_TERMS = Field(
        default_factory=WESTHUYSEN,
        description="SWAN source terms to be used",
        discriminator="model_type",
    )

    @root_validator
    def check_source_terms(cls, values):
        return values

    def cmd(self):
        repr = f"GEN3 {self.source_terms.render()}"
        return repr


# =====================================================================================
# Swell dissipation SSWELL
# =====================================================================================
class NEGATINP(BaseComponent):
    """Negative wind input.

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

    """

    model_type: Literal["negatinp"] = Field(
        default="negatinp", description="Model type discriminator"
    )
    rdcoef: confloat(ge=0.0, le=1.0) = Field(
        default=0.0,
        description="Coefficient representing the strength of negative wind input",
    )

    def cmd(self) -> str:
        return f"NEGATINP rdcoef={self.rdcoef}"


class SSWELL(BaseComponent):
    """Swell dissipation sub-component.

    `SSWELL base component.`

    With this command the user can influence the type of swell dissipation included in
    the computations. The Zieger option is intended for use with negative wind input
    via the NEGATINP command. Zieger non-breaking dissipation follows the method used
    in WAVEWATCH III version 4 and does not include the steepness-dependent swell
    coefficient introduced in WAVEWATCH III version 5. As noted already, if
    `GEN3 ST6...` command is used, this SSWELL command should be provided.

    """

    model_type: Literal["sswell"] = Field(
        default="sswell", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return "SSWELL"


class ROGERS(SSWELL):
    """Nonbreaking dissipation of Rogers et al. (2012).

    References
    ----------
    Rogers, W.E., Babanin, A.V. and Wang, D.W., 2012. Observation-consistent input and
    whitecapping dissipation in a model for wind-generated surface waves: Description
    and simple calculations. Journal of Atmospheric and Oceanic Technology, 29(9),
    pp.1329-1346.

    """

    model_type: Literal["rogers"] = Field(
        default="rogers", description="Model type discriminator"
    )
    cdsv: Optional[float] = Field(
        description=(
            "Coefficient related to laminar atmospheric boundary layer "
            "(SWAN default: 1.2)"
        )
    )
    feswell: Optional[float] = Field(description="Swell dissipation factor")

    def cmd(self) -> str:
        repr = f"{super().cmd()} ROGERS"
        if self.cdsv is not None:
            repr += f" cdsv={self.cdsv}"
        if self.feswell is not None:
            repr += f" feswell={self.feswell}"
        return repr


class ARDHUIN(SSWELL):
    """Nonbreaking dissipation of Ardhuin et al. (2010).

    References
    ----------
    Ardhuin, F., Rogers, E., Babanin, A.V., Filipot, J.F., Magne, R., Roland, A.,
    Van Der Westhuysen, A., Queffeulou, P., Lefevre, J.M., Aouf, L. and Collard, F.,
    2010. Semiempirical dissipation source functions for ocean waves. Part I:
    Definition, calibration, and validation. Journal of Physical Oceanography, 40(9),
    pp.1917-1941.

    """

    model_type: Literal["ardhuin"] = Field(
        default="ardhuin", description="Model type discriminator"
    )
    cdsv: Optional[float] = Field(
        description=(
            "Coefficient related to laminar atmospheric boundary layer "
            "(SWAN default: 1.2)"
        )
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} ARDHUIN"
        if self.cdsv is not None:
            repr += f" cdsv={self.cdsv}"
        return repr


class ZIEGER(SSWELL):
    """Nonbreaking dissipation of Zieger et al. (2015).

    Swell dissipation of Young et al. (2013) updated by Zieger et al. (2015).

    References
    ----------
    Zieger, S., Babanin, A.V., Rogers, W.E. and Young, I.R., 2015. Observation-based
    source terms in the third-generation wave model WAVEWATCH. Ocean Modelling, 96,
    pp.2-25.

    Young, I.R., Babanin, A.V. and Zieger, S., 2013. The decay rate of ocean swell
    observed by altimeter. Journal of physical oceanography, 43(11), pp.2322-2333.

    """

    model_type: Literal["zieger"] = Field(
        default="zieger", description="Model type discriminator"
    )
    b1: Optional[float] = Field(
        description="Non-dimensional proportionality coefficient"
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} ZIEGER"
        if self.b1 is not None:
            repr += f" b1={self.b1}"
        return repr


# =====================================================================================
# WCAPPING
# =====================================================================================
class WCAPKOMEN(BaseComponent):
    """Whitecapping according to Komen (1984).

    `WCAPPING KOMEN [cds2] [stpm] [powst] [delta] [powk]`

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

    """

    model_type: Literal["wcapkomen"] = Field(
        default="wcapkomen", description="Model type discriminator"
    )
    cds2: Optional[float] = Field(
        description=(
            "Coefficient for determining the rate of whitecapping dissipation ($Cds$) "
            "(SWAN default: 2.36e-5)"
        )
    )
    stpm: Optional[float] = Field(
        description=(
            "Value of the wave steepness for a Pierson-Moskowitz spectrum "
            "($s^2_{PM}$) (SWAN default: 3.02e-3)"
        )
    )
    powst: Optional[float] = Field(
        description=(
            "Power of steepness normalized with the wave steepness "
            "of a Pierson-Moskowitz spectrum (SWAN default: 2)"
        )
    )
    delta: Optional[float] = Field(
        description=(
            "Coefficient which determines the dependency of the whitecapping "
            "on wave number (SWAN default: 1)"
        )
    )
    powk: Optional[float] = Field(
        description=(
            "power of wave number normalized with the mean wave number "
            "(SWAN default: 1)"
        )
    )

    def cmd(self) -> str:
        repr = f"WCAPPING KOMEN"
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


class WCAPAB(BaseComponent):
    """Whitecapping according to Alves and Banner (2003).

    `WCAPPING AB [cds2] [br] CURRENT [cds3]`

    References
    ----------
    Alves, J.H.G. and Banner, M.L., 2003. Performance of a saturation-based
    dissipation-rate source term in modeling the fetch-limited evolution of wind waves.
    Journal of Physical Oceanography, 33(6), pp.1274-1298.

    """

    model_type: Literal["wcapab"] = Field(
        default="wcapab", description="Model type discriminator"
    )
    cds2: Optional[float] = Field(
        description=(
            "proportionality coefficient due to Alves and Banner (2003) "
            "(SWAN default: 5.0e-5)"
        )
    )
    br: Optional[float] = Field(
        description="Threshold saturation level	(SWAN default: 1.75e-3)"
    )
    current: bool = Field(
        default=False,
        description=(
            "Indicates that enhanced current-induced dissipation "
            "as proposed by Van der Westhuysen (2012) is to be added"
        ),
    )
    cds3: Optional[float] = Field(
        description="Proportionality coefficient (SWAN default: 0.8)"
    )

    def cmd(self) -> str:
        repr = f"WCAPPING AB"
        if self.cds2 is not None:
            repr += f" cds2={self.cds2}"
        if self.br is not None:
            repr += f" br={self.br}"
        if self.current:
            repr += f" CURRENT"
        if self.cds3 is not None:
            repr += f" cds3={self.cds3}"
        return repr


# =====================================================================================
# QUADRUPL
# =====================================================================================
class QUADRUPL(BaseComponent):
    """Nonlinear quadruplet wave interactions.

    `QUADRUPL [iquad] [lambda] [Cnl4] [Csh1] [Csh2] [Csh3]`

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

    """

    model_type: Literal["quadrupl"] = Field(
        default="quadrupl", description="Model type discriminator"
    )
    iquad: Literal[1, 2, 3, 8, 4, 51, 52, 53] = Field(
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
        description=(
            "Coefficient for quadruplet configuration in case of DIA "
            "(SWAN default: 0.25)"
        ),
    )
    cn14: Optional[float] = Field(
        description=(
            "Proportionality coefficient for quadruplet interactions in case of DIA "
            "(SWAN default: 3.0e7"
        ),
    )
    csh1: Optional[float] = Field(
        description=(
            "Coefficient for shallow water scaling in case of DIA (SWAN default: 5.5)"
        ),
    )
    csh2: Optional[float] = Field(
        description=(
            "Coefficient for shallow water scaling in case of DIA "
            "(SWAN default: 0.833333)"
        ),
    )
    csh3: Optional[float] = Field(
        description=(
            "Coefficient for shallow water scaling in case of DIA "
            "(SWAN default: -1.25)"
        ),
    )

    def cmd(self) -> str:
        repr = f"QUADRUPL"
        if self.iquad is not None:
            repr += f" iquad={self.iquad}"
        if self.lambd is not None:
            repr += f" lambda={self.lambd}"
        if self.cn14 is not None:
            repr += f" Cn14={self.cn14}"
        if self.csh1 is not None:
            repr += f" Csh1={self.csh1}"
        if self.csh2 is not None:
            repr += f" Csh2={self.csh2}"
        if self.csh3 is not None:
            repr += f" Csh3={self.csh3}"
        return repr


# =====================================================================================
# BREAKING
# =====================================================================================
class BREAKCONSTANT(BaseComponent):
    """Constant wave breaking index.

    `BREAKING CONSTANT [alpha] [gamma]`

    Indicates that a constant breaker index is to be used.

    """

    model_type: Literal["constant"] = Field(
        default="constant", description="Model type discriminator"
    )
    alpha: Optional[float] = Field(
        description=(
            "Proportionality coefficient of the rate of dissipation "
            "(SWAN default: 1.0)"
        )
    )
    gamma: Optional[float] = Field(
        description=(
            "The breaker index, i.e. the ratio of maximum individual wave height "
            "over depth (SWAN default: 0.73)"
        )
    )

    def cmd(self) -> str:
        repr = "BREAKING CONSTANT"
        if self.alpha is not None:
            repr += f" alpha={self.alpha}"
        if self.gamma is not None:
            repr += f" gamma={self.gamma}"
        return repr


class BREAKBKD(BaseComponent):
    """Variable wave breaking index.

    `BREAKING BKD [alpha] [gamma0] [a1] [a2] [a3]`

    Indicates that the breaker index scales with both the bottom slope ($beta$) and the
    dimensionless depth (kd).

    """

    model_type: Literal["bkd"] = Field(
        default="bkd", description="Model type discriminator"
    )
    alpha: Optional[float] = Field(
        description=(
            "Proportionality coefficient of the rate of dissipation "
            "(SWAN default: 1.0)"
        )
    )
    gamma0: Optional[float] = Field(
        description=("The reference $gamma$ for horizontal slopes (SWAN default: 0.54)")
    )
    a1: Optional[float] = Field(
        description=(
            "First tunable coefficient for the breaker index (SWAN default: 7.59)"
        )
    )
    a2: Optional[float] = Field(
        description=(
            "Second tunable coefficient for the breaker index (SWAN default: -8.06)"
        )
    )
    a3: Optional[float] = Field(
        description=(
            "Third tunable coefficient for the breaker index (SWAN default: 8.09)"
        )
    )

    def cmd(self) -> str:
        repr = "BREAKING BKD"
        if self.alpha is not None:
            repr += f" alpha={self.alpha}"
        if self.gamma0 is not None:
            repr += f" gamma0={self.gamma0}"
        if self.a1 is not None:
            repr += f" a1={self.a1}"
        if self.a2 is not None:
            repr += f" a2={self.a2}"
        if self.a3 is not None:
            repr += f" a3={self.a3}"
        return repr


# =====================================================================================
# FRICTION
# =====================================================================================
class JONSWAP(BaseComponent):
    """Hasselmann et al. (1973) Jonswap friction.

    `FRICTION JONSWAP CONSTANT [cfjon]`

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

    TODO: Implement VARIABLE option?

    """

    model_type: Literal["jonswap"] = Field(
        default="jonswap", description="Model type discriminator"
    )
    cfjon: Optional[float] = Field(
        description="Coefficient of the JONSWAP formulation (SWAN default: 0.038)"
    )

    def cmd(self) -> str:
        repr = "FRICTION JONSWAP CONSTANT"
        if self.cfjon is not None:
            repr += f" cfjon={self.cfjon}"
        return repr


class COLLINS(BaseComponent):
    """Collins (1972) friction.

    `FRICTION COLLINS [cfw]`

    Note that `cfw` is allowed to vary over the computational region; in that case use
    the commands INPGRID FRICTION and READINP FRICTION to define and read the friction
    data. This command FRICTION is still required to define the type of friction
    expression. The value of `cfw` in this command is then not required (it will be
    ignored).

    References
    ----------
    Collins, J.I., 1972. Prediction of shallow-water spectra. Journal of Geophysical
    Research, 77(15), pp.2693-2707.

    """

    model_type: Literal["collins"] = Field(
        default="collins", description="Model type discriminator"
    )
    cfw: Optional[float] = Field(
        description="Collins bottom friction coefficient (SWAN default: 0.015)"
    )

    def cmd(self) -> str:
        repr = "FRICTION COLLINS"
        if self.cfw is not None:
            repr += f" cfw={self.cfw}"
        return repr


class MADSEN(BaseComponent):
    """Madsen et al (1988) friction.

    `FRICTION MADSEN [kn]`

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

    """

    model_type: Literal["madsen"] = Field(
        default="madsen", description="Model type discriminator"
    )
    kn: Optional[float] = Field(
        description=(
            "equivalent roughness length scale of the bottom (in m) "
            "(SWAN default: 0.05)"
        )
    )

    def cmd(self) -> str:
        repr = "FRICTION MADSEN"
        if self.kn is not None:
            repr += f" kn={self.kn}"
        return repr


class RIPPLES(BaseComponent):
    """Smith et al. (2011) Ripples friction.

    `FRICTION RIPPLES [S] [D]`

    Indicates that the expression of Smith et al. (2011) should be activated. Here
    friction depends on the formation of bottom ripples and sediment size.

    References
    ----------
    Smith, G.A., Babanin, A.V., Riedel, P., Young, I.R., Oliver, S. and Hubbert, G.,
    2011. Introduction of a new friction routine into the SWAN model that evaluates
    roughness due to bedform and sediment size changes. Coastal Engineering, 58(4),
    pp.317-326.

    """

    model_type: Literal["ripples"] = Field(
        default="ripples", description="Model type discriminator"
    )
    s: Optional[float] = Field(
        description="The specific gravity of the sediment (SWAN default: 2.65)"
    )
    d: Optional[float] = Field(
        description="The sediment diameter (in m) (SWAN default: 0.0001)"
    )

    def cmd(self) -> str:
        repr = "FRICTION RIPPLES"
        if self.s is not None:
            repr += f" S={self.s}"
        if self.d is not None:
            repr += f" D={self.d}"
        return repr


# =====================================================================================
# TRIAD
# =====================================================================================
class TRIAD(BaseComponent):
    """Wave triad interactions.

    `TRIAD`

    With this command the user can activate the triad wave-wave interactions. If this
    command is not used, SWAN will not account for triads.

    """

    model_type: Literal["triad"] = Field(
        default="triad", description="Model type discriminator"
    )
    biphase: Union[ELDEBERKY, DEWIT] = Field(
        default_factory=ELDEBERKY,
        description="Defines the parameterization of biphase (self-self interaction)",
    )

    def cmd(self) -> str:
        return f"TRIAD"


class DCTA(TRIAD):
    """Triad interactions with the DCTA method of Booij et al. (2009).

    `TRIAD DCTA [trfac] [p] COLL|NONC BIPHHASE ELDEBERKY|DEWIT`

    References
    ----------
    Booij, N., Holthuijsen, L.H. and Bénit, M.P., 2009. A distributed collinear triad
    approximation in SWAN. In Proceedings Of Coastal Dynamics 2009: Impacts of Human
    Activities on Dynamic Coastal Processes (With CD-ROM) (pp. 1-10).

    """

    model_type: Literal["dcta"] = Field(
        default="dcta", description="Model type discriminator"
    )
    trfac: Optional[float] = Field(
        description=(
            "Scaling factor that controls the intensity of "
            "the triad interaction due to DCTA (SWAN default: 4.4)"
        ),
    )
    p: Optional[float] = Field(
        description=(
            "Shape coefficient to force the high-frequency tail" "(SWAN default: 4/3)"
        ),
    )
    noncolinear: bool = Field(
        default=False,
        description=(
            "If True, the noncolinear triad interactions "
            "with the DCTA framework are accounted for"
        ),
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} DCTA"
        if self.trfac is not None:
            repr += f" trfac={self.trfac}"
        if self.p is not None:
            repr += f" p={self.p}"
        if self.noncolinear:
            repr += " NONC"
        else:
            repr += " COLL"
        repr += f" {self.biphase.render()}"
        return repr


class LTA(TRIAD):
    """Triad interactions with the LTA method of Eldeberky (1996).

    `TRIAD LTA [trfac] [cutfr] BIPHHASE ELDEBERKY|DEWIT`

    References
    ----------
    Eldeberky, Y., Polnikov, V. and Battjes, J.A., 1996. A statistical approach for
    modeling triad interactions in dispersive waves. In Coastal Engineering 1996
    (pp. 1088-1101).

    """

    model_type: Literal["lta"] = Field(
        default="lta", description="Model type discriminator"
    )
    trfac: Optional[float] = Field(
        description=(
            "Scaling factor that controls the intensity of "
            "the triad interaction due to LTA (SWAN default: 0.8)"
        ),
    )
    cutfr: Optional[float] = Field(
        description=(
            "Controls the maximum frequency that is considered in the LTA "
            "computation. The value of `cutfr` is the ratio of this maximum "
            "frequency over the mean frequency (SWAN default: 2.5)"
        ),
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} LTA"
        if self.trfac is not None:
            repr += f" trfac={self.trfac}"
        if self.cutfr is not None:
            repr += f" cutfr={self.cutfr}"
        repr += f" {self.biphase.render()}"
        return repr


class SPB(TRIAD):
    """Triad interactions according to the SPB method of Becq-Girard et al. (1999).

    `TRIAD SPB [trfac] [a] [b] BIPHHASE ELDEBERKY|DEWIT`

    References
    ----------
    Becq-Girard, F., Forget, P. and Benoit, M., 1999. Non-linear propagation of
    unidirectional wave fields over varying topography. Coastal Engineering, 38(2),
    pp.91-113.

    """

    model_type: Literal["spb"] = Field(
        default="spb", description="Model type discriminator"
    )
    trfac: Optional[float] = Field(
        description=(
            "Scaling factor that controls the intensity of "
            "the triad interaction due to SPB (SWAN default: 0.9)"
        ),
    )
    a: Optional[float] = Field(
        description=(
            "First calibration parameter for tuning K in Eq. (5.1) of "
            "Becq-Girard et al. (1999). This parameter is associated with broadening "
            "of the resonance condition. The default value is 0.95 and is calibrated "
            "by means of laboratory experiments (SWAN default: 0.95)"
        ),
    )
    b: Optional[float] = Field(
        description=(
            "Second calibration parameter for tuning K in Eq. (5.1) of "
            "Becq-Girard et al. (1999). This parameter is associated with broadening "
            "of the resonance condition. The default value is -0.75 and is calibrated "
            "by means of laboratory experiments. However, it may not be appropriate "
            "for true 2D field cases as it does not scale with the wave field "
            "characteristics. Hence, this parameter is set to zero (SWAN default: 0.0)"
        ),
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} SPB"
        if self.trfac is not None:
            repr += f" trfac={self.trfac}"
        if self.a is not None:
            repr += f" a={self.a}"
        if self.b is not None:
            repr += f" b={self.b}"
        repr += f" {self.biphase.render()}"
        return repr


# =====================================================================================
# VEGETATION
# =====================================================================================
class VEGETATION(BaseComponent): 
    """Vegetation dumping.

    `VEGETATION [iveg] < [height] [diamtr] [nstems] [drag] >`

    With this command the user can activate wave damping due to vegetation based on the
    Dalrymple's formula (1984) as implemented by Suzuki et al. (2011). This damping is
    uniform over the wave frequencies. An alternative is the frequency-dependent
    (canopy) dissipation model of Jacobsen et al. (2019). If this command is not used,
    SWAN will not account for vegetation effects.

    The vegetation (rigid plants) can be divided over a number of vertical segments and
    so, the possibility to vary the vegetation vertically is included. Each vertical
    layer represents some characteristics of the plants. These variables as indicated
    below can be repeated as many vertical layers to be chosen.

    References
    ----------
    Dalrymple, R.A., Kirby, J.T. and Hwang, P.A., 1984. Wave diffraction due to areas
    of energy dissipation. Journal of waterway, port, coastal, and ocean engineering,
    110(1), pp.67-79.

    Jacobsen, N.G., Bakker, W., Uijttewaal, W.S. and Uittenbogaard, R., 2019.
    Experimental investigation of the wave-induced motion of and force distribution
    along a flexible stem. Journal of Fluid Mechanics, 880, pp.1036-1069.

    Suzuki, T., Zijlema, M., Burger, B., Meijer, M.C. and Narayan, S., 2012. Wave
    dissipation by vegetation with layer schematization in SWAN. Coastal Engineering,
    59(1), pp.64-71.

    Notes
    -----
    Vertical layering of the vegetation is not yet implemented for the
    Jacobsen et al. (2019) method.

    """

    model_type: Literal["vegetation"] = Field(
        default="vegetation", description="Model type discriminator"
    )
    iveg: Literal[1, 2] = Field(
        default=1,
        description=(
            "Indicates the method for the vegetation computation (SWAN default: 1):\n"
            "\n* 1: Suzuki et al. (2011)\n* 2: Jacobsen et al. (2019)\n"
        ),
    )
    height: Union[float, list[float]] = Field(
        description="The plant height per layer (in m)"
    )
    diamtr: Union[float, list[float]] = Field(
        description="The diameter of each plant stand per layer (in m)"
    )
    drag: Union[float, list[float]] = Field(
        description="The drag coefficient per layer"
    )
    nstems: Union[int, list[int]] = Field(
        default=1,
        description=(
            "The number of plant stands per square meter for each layer. Note that "
            "`nstems` is allowed to vary over the computational region to account for "
            "the zonation of vegetation. In that case use the commands "
            "`IMPGRID NPLANTS` and `READINP NPLANTS` to define and read the "
            "vegetation density. The (vertically varying) value of `nstems` in this "
            "command will be multiplied by this horizontally varying plant density "
            "(SWAN default: 1)"
        ),
    )

    @root_validator
    def number_of_layers(cls, values):
        """Assert that the number of layers is the same for all variables."""
        sizes = {}
        for key in ["height", "diamtr", "drag", "nstems"]:
            if values.get(key) is None:
                continue
            elif not isinstance(values.get(key), list):
                values[key] = [values[key]]
            sizes.update({key: len(values[key])})
        if len(set(sizes.values())) > 1:
            raise ValueError(
                "The number of layers must be the same for all variables. "
                f"Got these number of layers: {sizes}"
            )
        if values.get("iveg", 1) == 2 and sizes.get("nstems", 1) > 1:
            logger.warning(
                "Vertical layering of the vegetation is not yet implemented for the "
                "Jacobsen et al. (2019) method, please define single layer"
            )
        return values

    def cmd(self) -> str:
        repr = f"VEGETATION iveg={self.iveg}"
        for h, d, dr, n in zip(self.height, self.diamtr, self.drag, self.nstems):
            repr += f" height={h} diamtr={d} nstems={n} drag={dr}"
        return repr


# =====================================================================================
# MUD
# =====================================================================================
class MUD(BaseComponent):
    """Mud dumping.

    `MUD [layer] [rhom] [viscm]`

    With this command the user can activate wave damping due to mud based on Ng (2000).
    If this command or the commands INPGRID MUDLAY and READINP MUDLAY are not used,
    SWAN will not account for muddy bottom effects.

    References
    ----------
    Ng, C., 2000, Water waves over a muddy bed: A two layer Stokes' boundary layer
    model, Coastal Eng., 40, 221-242.

    TODO: Validate `layer` must be prescribed if `INPGRID MUDLAY` isn't used.

    """

    model_type: Literal["mud"] = Field(
        default="mud", description="Model type discriminator"
    )
    layer: Optional[float] = Field(
        description=(
            "The thickness of the mud layer (in m). Note that `layer` is allowed to "
            "vary over the computational region to account for the zonation of muddy "
            "bottom. In that case use the commands `INPGRID MUDLAY` and `READINP "
            "MUDLAY` to define and read the layer thickness of mud. The value of "
            "`layer` in this command is then not required (it will be ignored)"
        ),
    )
    rhom: Optional[float] = Field(
        description="The density of the mud layer (in kg/m3) (SWAN default: 1300)"
    )
    viscm: Optional[float] = Field(
        description=(
            "The kinematic viscosity of the mud layer (in m2/s) (SWAN default: 0.0076)"
        ),
    )

    def cmd(self) -> str:
        repr = "MUD"
        if self.layer is not None:
            repr += f" layer={self.layer}"
        if self.rhom is not None:
            repr += f" rhom={self.rhom}"
        if self.viscm is not None:
            repr += f" viscm={self.viscm}"
        return repr


# =====================================================================================
# SICE
# =====================================================================================
class SICE(BaseComponent):
    """Sea ice dissipation default.

    `SICE [aice]`

    Using this command, the user activates a sink term to represent the dissipation of
    wave energy by sea ice. The default method is R19 empirical/parametric: a
    polynomial based on wave frequency (Rogers, 2019). This polynomial (in 1/m) has
    seven dimensional coefficients; see Scientific/Technical documentation for details.
    If this command is not used, SWAN will not account for sea ice effects.

    References
    ----------
    Doble, M.J., De Carolis, G., Meylan, M.H., Bidlot, J.R. and Wadhams, P., 2015.
    Relating wave attenuation to pancake ice thickness, using field measurements and
    model results. Geophysical Research Letters, 42(11), pp.4473-4481.

    Meylan, M.H., Bennetts, L.G. and Kohout, A.L., 2014. In situ measurements and
    analysis of ocean waves in the Antarctic marginal ice zone. Geophysical Research
    Letters, 41(14), pp.5046-5051.

    Rogers, W.E., Meylan, M.H. and Kohout, A.L., 2018. Frequency distribution of
    dissipation of energy of ocean waves by sea ice using data from Wave Array 3 of
    the ONR “Sea State” field experiment. Nav. Res. Lab. Memo. Rep, pp.18-9801.

    Rogers, W.E., Meylan, M.H. and Kohout, A.L., 2021. Estimates of spectral wave
    attenuation in Antarctic sea ice, using model/data inversion. Cold Regions Science
    and Technology, 182, p.103198.

    Notes
    -----
    Iis also necessary to describe the ice, using the `ICE` command (for uniform and
    stationary ice) or `INPGRID`/`READINP` commands (for variable ice).

    TODO: Verify if the `aice` parameter should be used with SICE command, it is not
    shown in the command tree but it is described as an option in the description.

    """

    model_type: Literal["sice", "SICE"] = Field(
        default="sice", description="Model type discriminator"
    )
    aice: Optional[float] = Field(
        description=(
            "Ice concentration as a fraction from 0 to 1. Note that `aice` is allowed "
            "to vary over the computational region to account for the zonation of ice "
            "concentration. In that case use the commands `INPGRID AICE` and `READINP "
            "AICE` to define and read the sea concentration. The value of `aice` in "
            "this command is then not required (it will be ignored)"
        ),
        ge=0.0,
        le=1.0,
    )

    def cmd(self) -> str:
        repr = "SICE"
        if self.aice is not None:
            repr += f" aice={self.aice}"
        return repr


class R19(SICE):
    """Sea ice dissipation based on the empirical polynomial of Rogers et al (2019).

    `SICE [aice] R19 [c0] [c1] [c2] [c3] [c4] [c5] [c6]`

    The default options recover the polynomial of Meylan et al. (2014), calibrated for
    a case of ice floes, mostly 10 to 25 m in diameter, in the marginal ice zone near
    Antarctica. Examples for other calibrations can be found in the
    Scientific/Technical documentation.

    References
    ----------
    Meylan, M.H., Bennetts, L.G. and Kohout, A.L., 2014. In situ measurements and
    analysis of ocean waves in the Antarctic marginal ice zone. Geophysical Research
    Letters, 41(14), pp.5046-5051.

    Rogers, W.E., Meylan, M.H. and Kohout, A.L., 2018. Frequency distribution of
    dissipation of energy of ocean waves by sea ice using data from Wave Array 3 of
    the ONR “Sea State” field experiment. Nav. Res. Lab. Memo. Rep, pp.18-9801.

    """

    model_type: Literal["r19", "R19"] = Field(
        default="r19", description="Model type discriminator"
    )
    c0: Optional[float] = Field(
        description=(
            "Polynomial coefficient (in 1/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )
    c1: Optional[float] = Field(
        description=(
            "Polynomial coefficient (in s/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )
    c2: Optional[float] = Field(
        description=(
            "Polynomial coefficient (in s2/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 1.06E-3)"
        ),
    )
    c3: Optional[float] = Field(
        description=(
            "Polynomial coefficient (in s3/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )
    c4: Optional[float] = Field(
        description=(
            "Polynomial coefficient (in s4/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 2.3E-2)"
        ),
    )
    c5: Optional[float] = Field(
        description=(
            "Polynomial coefficient (in s5/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )
    c6: Optional[float] = Field(
        description=(
            "Polynomial coefficient (in s6/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} {self.model_type.upper()}"
        if self.c0 is not None:
            repr += f" c0={self.c0}"
        if self.c1 is not None:
            repr += f" c1={self.c1}"
        if self.c2 is not None:
            repr += f" c2={self.c2}"
        if self.c3 is not None:
            repr += f" c3={self.c3}"
        if self.c4 is not None:
            repr += f" c4={self.c4}"
        if self.c5 is not None:
            repr += f" c5={self.c5}"
        if self.c6 is not None:
            repr += f" c6={self.c6}"
        return repr


class D15(SICE):
    """Sea ice dissipation based on the method of Doble et al. (2015).

    `SICE [aice] D15 [chf]`

    References
    ----------
    Doble, M.J., De Carolis, G., Meylan, M.H., Bidlot, J.R. and Wadhams, P., 2015.
    Relating wave attenuation to pancake ice thickness, using field measurements and
    model results. Geophysical Research Letters, 42(11), pp.4473-4481.

    """

    model_type: Literal["d15", "D15"] = Field(
        default="d15", description="Model type discriminator"
    )
    chf: Optional[float] = Field(
        description="A simple coefficient of proportionality (SWAN default: 0.1)",
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} {self.model_type.upper()}"
        if self.chf is not None:
            repr += f" chf={self.chf}"
        return repr


class M18(SICE):
    """Sea ice dissipation based on the method of Meylan et al. (2018).

    `SICE [aice] M18 [chf]`

    References
    ----------
    Meylan, M.H., Bennetts, L.G. and Kohout, A.L., 2014. In situ measurements and
    analysis of ocean waves in the Antarctic marginal ice zone. Geophysical Research
    Letters, 41(14), pp.5046-5051.

    """

    model_type: Literal["m18", "M18"] = Field(
        default="m18", description="Model type discriminator"
    )
    chf: Optional[float] = Field(
        description="A simple coefficient of proportionality (SWAN default: 0.059)",
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} {self.model_type.upper()}"
        if self.chf is not None:
            repr += f" chf={self.chf}"
        return repr


class R21B(SICE):
    """Sea ice dissipation based on the method of Rogers et al. (2021).

    `SICE [aice] R21B [chf] [npf]`

    References
    ----------
    Rogers, W.E., Meylan, M.H. and Kohout, A.L., 2021. Estimates of spectral wave
    attenuation in Antarctic sea ice, using model/data inversion. Cold Regions Science
    and Technology, 182, p.103198.

    """

    model_type: Literal["r21b", "R21B"] = Field(
        default="r21b", description="Model type discriminator"
    )
    chf: Optional[float] = Field(
        description="A simple coefficient of proportionality (SWAN default: 2.9)",
    )
    npf: Optional[float] = Field(
        description=(
            "Controls the degree of dependence on frequency and ice thickness "
            "(SWAN default: 4.5)"
        ),
    )

    def cmd(self) -> str:
        repr = f"{super().cmd()} {self.model_type.upper()}"
        if self.chf is not None:
            repr += f" chf={self.chf}"
        if self.npf is not None:
            repr += f" npf={self.npf}"
        return repr


# =====================================================================================
# TURBULENCE
# =====================================================================================
class TURBULENCE(BaseComponent):
    """Turbulent viscosity.

    `TURBULENCE`

    With this optional command the user can activate turbulent viscosity. This physical
    effect is also activated by reading values of the turbulent viscosity using the
    `READGRID TURB` command, but then with the default value of `ctb`. The command
    `READGRID TURB` is necessary if this command `TURB` is used since the value of the
    viscosity is assumed to vary over space.

    """

    model_type: Literal["turbulence", "TURBULENCE"] = Field(
        default="turbulence", description="Model type discriminator"
    )
    ctb: Optional[float] = Field(
        description=(
            "The value of the proportionality coefficient appearing in the energy "
            "dissipation term (SWAN default: 0.01)"
        ),
    )
    current: Optional[bool] = Field(
        default=True,
        description=(
            "If this keyword is present the turbulent viscosity will be derived from "
            "the product of the depth and the absolute value of the current velocity. "
            "If the command `READGRID TURB` is used, this option is ignored; "
            "the values read from file will prevail"
        ),
    )
    tbcur: Optional[float] = Field(
        description=(
            "The factor by which depth x current velocity is multiplied in order to "
            "get the turbulent viscosity (SWAN default: 0.004)"
        ),
    )

    @validator("tbcur", pre=False)
    def tbcur_only_with_current(cls, value, values):
        if values.get("current") == False and value is not None:
            raise ValueError(
                "`tbcur` keyword can only be defined if `current` is True"
            )
        return value

    def cmd(self) -> str:
        repr = "TURBULENCE"
        if self.ctb is not None:
            repr += f" ctb={self.ctb}"
        if self.current:
            repr += " CURRENT"
        if self.tbcur is not None:
            repr += f" tbcur={self.tbcur}"
        return repr


# =====================================================================================
# BRAGG
# =====================================================================================
class BRAGG(BaseComponent):
    """Bragg scattering.

    `BRAGG`

    Using this optional command, the user activates a source term to represent the
    scattering of waves due to changes in the small-scale bathymetry based on the
    theory of Ardhuin and Herbers (2002). If this command is not used, SWAN will not
    account for Bragg scattering.

    """

    model_type: Literal["bragg"] = Field(
        default="bragg", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return f"BRAGG"


# =====================================================================================
# LIMITER
# =====================================================================================
class LIMITER(BaseComponent):
    """Physics limiter.

    `LIMITER`

    With this command the user can de-activate permanently the quadruplets when
    the actual Ursell number exceeds `ursell`. Moreover, as soon as the actual
    fraction of breaking waves exceeds `qb` then the action limiter will not be
    used in case of decreasing action density.

    """

    model_type: Literal["limiter"] = Field(
        default="limiter", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return f"LIMITER"


# =====================================================================================
# OBSTACLE
# =====================================================================================
class OBSTACLE(BaseComponent):
    """Sub-grid obstacle.

    `OBSTACLE`

    With this optional command the user provides the characteristics of a (line
    of) sub-grid obstacle(s) through which waves are transmitted or against which
    waves are reflected (possibly both at the same time). The obstacle is sub-grid
    in the sense that it is narrow compared to the spatial meshes; its length should
    be at least one mesh length.

    """

    model_type: Literal["obstacle"] = Field(
        default="obstacle", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return f"OBSTACLE"


# =====================================================================================
# OBSTACLE FIG
# =====================================================================================
class OBSTACLE_FIG(BaseComponent):
    """Obstacle for free infragravity radiation.

    `OBSTACLE FIG`

    With this optional command the user specifies the obstacles along which the
    free infra-gravity (FIG) energy is radiated. By placing the obstacles close to
    the shorelines SWAN will include the FIG source term along the coastlines
    according to the parametrization of Ardhuin et al. (2014).

    References
    ----------
    Ardhuin, F., A. Rogers, A. Babanin, L. Filipot, A. Magne, A. Roland, and P.
    van der Westhuysen, Semiempirical Dissipation Source Functions for Ocean Waves.
    Part I: Definition, Calibration, and Validation, J. Phys. Oceanogr., 44(9),
    2352-2368, 2014.

    """

    model_type: Literal["obstacle_fig"] = Field(
        default="obstacle_fig", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return f"OBSTACLE FIG"


# =====================================================================================
# SETUP
# =====================================================================================
class SETUP(BaseComponent):
    """Wave setup.

    `SETUP`

    """

    model_type: Literal["setup"] = Field(
        default="setup", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return f"SETUP"


# =====================================================================================
# DIFFRACTION
# =====================================================================================
class DIFFRACTION(BaseComponent):
    """Wave diffraction.

    `DIFFRACTION`

    """

    model_type: Literal["diffraction"] = Field(
        default="diffraction", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return f"DIFFRACTION"


# =====================================================================================
# SURFBEAT
# =====================================================================================
class SURFBEAT(BaseComponent):
    """Surfbeat.

    `SURFBEAT`

    """

    model_type: Literal["surfbeat"] = Field(
        default="surfbeat", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return f"SURFBEAT"


# =====================================================================================
# SCAT
# =====================================================================================
class SCAT(BaseComponent):
    """Scattering.

    `SCAT`

    """

    model_type: Literal["scat"] = Field(
        default="scat", description="Model type discriminator"
    )

    def cmd(self) -> str:
        return f"SCAT"


# =====================================================================================
# Physics group component
# =====================================================================================
GEN_TYPE = Annotated[
    Union[GEN1, GEN2, GEN3],
    Field(description="Wave generation component", discriminator="model_type"),
]
SSWELL_TYPE = Annotated[
    Union[ROGERS, ARDHUIN, ZIEGER],
    Field(description="Swell dissipation component", discriminator="model_type"),
]
NEGATINP_TYPE = Annotated[
    NEGATINP,
    Field(description="Negative wind input component", discriminator="model_type"),
]
WCAPPING_TYPE = Annotated[
    Union[WCAPKOMEN, WCAPAB],
    Field(description="Whitecapping component", discriminator="model_type"),
]
QUADRUPL_TYPE = Annotated[
    QUADRUPL,
    Field(description="Quadruplet interactions component", discriminator="model_type"),
]
BREAKING_TYPE = Annotated[
    Union[BREAKCONSTANT, BREAKBKD],
    Field(description="Wave breaking component", discriminator="model_type"),
]
FRICTION_TYPE = Annotated[
    Union[JONSWAP, COLLINS, MADSEN, RIPPLES],
    Field(description="Bottom friction component", discriminator="model_type"),
]
TRIAD_TYPE = Annotated[
    Union[DCTA, LTA, SPB],
    Field(description="Triad interactions component", discriminator="model_type"),
]
VEGETATION_TYPE = Annotated[
    VEGETATION, Field(description="Vegetation component", discriminator="model_type")
]
MUD_TYPE = Annotated[
    MUD, Field(description="Mud component", discriminator="model_type")
]
SICE_TYPE = Annotated[
    Union[SICE, R19, D15, M18, R21B],
    Field(description="Sea ice component", discriminator="model_type")
]
TURBULENCE_TYPE = Annotated[
    TURBULENCE,
    Field(description="Turbulent dissipation component", discriminator="model_type"),
]


class PHYSICS(BaseComponent):
    """Physics group component.

    The physics group component is a convenience to allow specifying several individual
    components in a single command and check for consistency between them.

    """

    model_type: Literal["physics"] = Field(
        default="physics", description="Model type discriminator"
    )
    gen: Optional[GEN_TYPE]
    sswell: Optional[SSWELL_TYPE]
    negatinp: Optional[NEGATINP_TYPE]
    wcapping: Optional[WCAPPING_TYPE]
    quadrupl: Optional[QUADRUPL_TYPE]
    breaking: Optional[BREAKING_TYPE]
    friction: Optional[FRICTION_TYPE]
    triad: Optional[TRIAD_TYPE]
    vegetation: Optional[VEGETATION_TYPE]
    mud: Optional[MUD_TYPE]
    sice: Optional[SICE_TYPE]
    turbulence: Optional[TURBULENCE_TYPE]

    @root_validator
    def deactivate_physics(cls, values):
        return values

    @validator("negatinp", pre=False)
    def negatinp_only_with_zieger(cls, value, values):
        """Log a warning if NEGATINP is used with a non-ZIEGER SSWELL."""
        if values["sswell"] is None:
            logger.warning(
                "The negative wind input NEGATINP is only intended to use with the "
                "swell dissipation SSWELL ZIEGER but no SSWELL has been specified."
            )
        elif values["sswell"].model_type != "zieger":
            logger.warning(
                "The negative wind input NEGATINP is only intended to use with the "
                "swell dissipation SSWELL ZIEGER but "
                f"SSWELL {values['sswell'].model_type.upper()} has been specified."
            )
        return value

    def cmd(self):
        repr = [self.gen.render()]
        if self.sswell is not None:
            repr += [f"{self.sswell.render()}"]
        if self.negatinp is not None:
            repr += [self.negatinp.render()]
        if self.wcapping is not None:
            repr += [self.wcapping.render()]
        if self.quadrupl is not None:
            repr += [self.quadrupl.render()]
        if self.breaking is not None:
            repr += [self.breaking.render()]
        if self.friction is not None:
            repr += [self.friction.render()]
        if self.triad is not None:
            repr += [self.triad.render()]
        if self.vegetation is not None:
            repr += [self.vegetation.render()]
        if self.mud is not None:
            repr += [self.mud.render()]
        if self.sice is not None:
            repr += [self.sice.render()]
        if self.turbulence is not None:
            repr += [self.turbulence.render()]
        return repr
