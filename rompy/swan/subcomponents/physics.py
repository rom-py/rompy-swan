"""SWAN physics subcomponents."""
from typing import Literal, Optional
from pydantic import Field, root_validator, confloat
from abc import ABC

from rompy.swan.subcomponents.base import BaseSubComponent


#======================================================================================
# Source terms
#======================================================================================
class SourceTerms(BaseSubComponent, ABC):
    """Source term subcomponent base class."""

    wind_drag: Literal["wu", "fit"] = Field(
        default="wu",
        description="Indicates the wind drag formulation",
    )
    agrow: bool = Field(
        default=False,
        description="Activate the Cavaleri and Malanotte (1981) wave growth term",
    )
    a: Optional[float] = Field(
        default=0.0015,
        description="Proportionality coefficient when activating the Cavaleri and Malanotte (1981) wave growth term",
    )


class JANSSEN(SourceTerms):
    """Janssen source terms subcomponent.

    `JANSSEN [cds1] [delta]`

    References
    ----------
    Janssen, P.A.E.M., 1989: Wave induced stress and the drag of air flow
    over sea waves, J. Phys. Oceanogr., 19, 745-754.

    Janssen, P.A.E.M., 1991: Quasi-linear theory of wind-wave generation
    applied to wave forecasting, J. Phys. Oceanogr., 21, 1631-1642.

    """

    model_type: Literal["janssen"] = Field(
        default="janssen", description="Model type discriminator"
    )
    cds1: Optional[float] = Field(
        description="Coefficient for determining the rate of whitecapping dissipation ($Cds / s^4_{PM}$) (SWAN default: 4.5)"
    )
    delta: Optional[float] = Field(
        description="Coefficient which determines the dependency of the whitecapping on wave number (mix with Komen et al. formulation) (SWAN default: 0.5)"
    )

    def cmd(self):
        repr = "JANSSEN"
        if self.cds1 is not None:
            repr += f" cds1={self.cds1}"
        if self.delta is not None:
            repr += f" delta={self.delta}"
        repr += f" DRAG {self.wind_drag.upper()}"
        if self.agrow:
            repr += f" AGROW a={self.a}"
        return repr


class KOMEN(SourceTerms):
    """Komen source terms subcomponent.

    `KOMEN [cds2] [stpm]`

    References
    ----------
    Komen, G.J., S. Hasselmann, and K. Hasselmann, 1984: On the existence of a fully
    developed wind-sea spectrum, J. Phys. Oceanogr., 14, 1271-1285.

    """

    model_type: Literal["komen"] = Field(
        default="komen", description="Model type discriminator"
    )
    cds2: Optional[float] = Field(
        description="Coefficient for determining the rate of whitecapping dissipation ($Cds$) (SWAN default: 2.36e-5)"
    )
    stpm: Optional[float] = Field(
        description="Value of the wave steepness for a Pierson-Moskowitz spectrum ($s^2_{PM}$) (SWAN default: 3.02e-3)"
    )

    def cmd(self):
        repr = "KOMEN"
        if self.cds2 is not None:
            repr += f" cds2={self.cds2}"
        if self.stpm is not None:
            repr += f" stpm={self.stpm}"
        repr += f" DRAG {self.wind_drag.upper()}"
        if self.agrow:
            repr += f" AGROW a={self.a}"
        return repr


class WESTHUYSEN(SourceTerms):
    """Westhuysen source terms subcomponent.

    `WESTHUYSEN [cds2] [br]`

    Nonlinear saturation-based whitecapping combined with wind input of Yan (1987).

    Notes
    -----
    The two arguments are specified in the Appendix C of the User manual but not in the
    command description for WESTH in Section 4.5.4. They are also options in the
    WCAPPING command. It is not entirely clear if they should/could be specified here.

    References
    ----------
    Van der Westhuysen, A.J., M. Zijlema and J.A. Battjes, 2007: Nonlinear
    saturation-based whitecapping dissipation in SWAN for deep and shallow water,
    Coast. Engng, 54:2, 151-170.

    """

    model_type: Literal["westhuysen"] = Field(
        default="westhuysen", description="Model type discriminator"
    )
    cds2: Optional[float] = Field(
        description="proportionality coefficient due to Alves and Banner (2003) (SWAN default: 5.0e-5)."
    )
    br: Optional[float] = Field(
        description="Threshold saturation level	(SWAN default: 1.75e-3)"
    )

    def cmd(self):
        repr = "WESTHUYSEN"
        if self.cds2 is not None:
            repr += f" cds2={self.cds2}"
        if self.br is not None:
            repr += f" br={self.br}"
        repr += f" DRAG {self.wind_drag.upper()}"
        if self.agrow:
            repr += f" AGROW a={self.a}"
        return repr


class ST6(SourceTerms):
    """St6 source terms subcomponent.

    `ST6 [a1sds] [a2sds] [p1sds] [p2sds] UP|DOWN HWANG|FAN|ECMWF VECTAU|SCATAU `
    `    TRUE10|U10PROXY [windscaling] DEBIAS [cdfac]`

    wind input and whitecapping from Rogers et al. (2012) (RBW12).

    Notes
    -----
    The two arguments are specified in the Appendix C of the User manual but not in the
    command description for WESTH in Section 4.5.4. They are also options in the
    WCAPPING command. It is not entirely clear if they should/could be specified here.

    References
    ----------
    Rogers, W.E., A.V. Babanin and D.W. Wang, 2012: Observation-Consistent Input and
    Whitecapping Dissipation in a Model for Wind-Generated Surface Waves: Description
    and Simple Calculations, J. Atmos. Oceanic Technol., 29:9, 1329-1346.

    """

    model_type: Literal["st6"] = Field(
        default="st6", description="Model type discriminator"
    )
    a1sds: float = Field(
        description="Coefficient related to local dissipation term T1 (a1 in RBW12)"
    )
    a2sds: float = Field(
        description="Coefficient related to local dissipation term T2 (a2 in RBW12)"
    )
    p1sds: Optional[float] = Field(
        description="Power coefficient controlling strength of dissipation term T1 (L in RBW12, SWAN default: 4)"
    )
    p2sds: Optional[float] = Field(
        description="Power coefficient controlling strength of dissipation term T2 (M in RBW12, SWAN default: 4)"
    )
    normalization: Literal["up", "down"] = Field(
        default="up",
        description="Selection of normalization of exceedance level by ET(f) (`up`) or E(f) (`down`) as in RBW12 (right column, page 1333), `up` is default and strongly recommended",
    )
    wind_drag: Literal["hwang", "fan", "ecmwf"] = Field(
        default="hwang",
        description="Wind drag formula, `hwang` is the default and is unchanged from RBW12, `fan` is from Fan et al. (2012), `ecmwf` follows teh WAM Cycle 4 methodology",
    )
    tau: Literal["vectau", "scatau"] = Field(
        default="vectau",
        description="Use vector (vectau) or scalar (scatau) calculation for the wind strerss (Eq. 12 in RBW12), `vectau` is the default and strongly recommended",
    )
    u10: Literal["u10proxy", "true10"] = Field(
        default="u10proxy",
        description="Wind velocity definition",
    )
    windscaling: Optional[float] = Field(
        default=32.0,
        description="Factor to scale U10 with U* when using U10PROXY",
    )
    cdfac: Optional[confloat(gt=0.0)] = Field(
        description="Counter bias in the input wind fields by providing a multiplier on the drag coefficient",
    )

    @root_validator
    def debias_only_with_hwang(cls, values):
        debias = values.get("debias")
        wind_drag = values.get("wind_drag", "hwang")
        if debias is not None and wind_drag != "hwang":
            raise ValueError(
                f"Debias is only supported with hwang wind drag, not {wind_drag}"
            )
        return values

    @property
    def u10_cmd(self):
        if self.u10 == "true10":
            return "TRUE10"
        else:
            return f"U10PROXY windscaling={self.windscaling}"

    def cmd(self):
        repr = f"ST6 a1sds={self.a1sds} a2sds={self.a2sds}"
        if self.p1sds is not None:
            repr += f" p1sds={self.p1sds}"
        if self.p2sds is not None:
            repr += f" p2sds={self.p2sds}"
        repr += f" {self.normalization.upper()}"
        repr += f" {self.wind_drag.upper()}"
        repr += f" {self.tau.upper()}"
        repr += f" {self.u10_cmd}"
        if self.cdfac is not None:
            repr += f" DEBIAS cdfac={self.cdfac}"
        if self.agrow:
            repr += f" AGROW a={self.a}"
        return repr


class ST6C1(ST6):
    """First ST6 calibration settings defined in the SWAN user manual."""

    model_type: Literal["st6c1"] = Field(default="st6c1")
    a1sds: Literal[4.7e-7] = Field(default=4.7e-7)
    a2sds: Literal[6.6e-6] = Field(default=6.6e-6)
    p1sds: Literal[4.0] = Field(default=4.0)
    p2sds: Literal[4.0] = Field(default=4.0)
    windscaling: Literal[28.0] = Field(default=28.0)
    agrow: Literal[True] = Field(default=True)


class ST6C2(ST6C1):
    """Second ST6 calibration settings defined in the SWAN user manual."""

    model_type: Literal["st6c2"] = Field(default="st6c2")
    wind_drag: Literal["fan"] = Field(default="fan")


class ST6C3(ST6C1):
    """Third ST6 calibration settings defined in the SWAN user manual."""

    model_type: Literal["st6c3"] = Field(default="st6c3")
    a1sds: Literal[2.8e-6] = Field(default=2.8e-6)
    a2sds: Literal[3.5e-5] = Field(default=3.5e-5)
    windscaling: Literal[32.0] = Field(default=32.0)


class ST6C4(ST6C3):
    """Forth ST6 calibration settings defined in the SWAN user manual."""

    model_type: Literal["st6c4"] = Field(default="st6c4")
    cdfac: Literal[0.89] = Field(default=0.89)


class ST6C5(ST6C1):
    """Fifth ST6 calibration settings defined in the SWAN user manual."""

    model_type: Literal["st6c5"] = Field(default="st6c5")
    cdfac: Literal[0.89] = Field(default=0.89)
    a1sds: Literal[6.5e-6] = Field(default=6.5e-6)
    a2sds: Literal[8.5e-5] = Field(default=8.5e-5)
    windscaling: Literal[35.0] = Field(default=35.0)


class NEGATINP(BaseSubComponent):
    """Nonbreaking dissipation of Young et al. (2013) updated by Zieger et al. (2015).

    With this optional command the user activates negative wind input. This is intended
    only for use with non-breaking swell dissipation SSWELL ZIEGER. Parameter `rdcoef`
    is a fraction between 0 and 1, representing the strength of negative wind input. As
    an example, with [rdcoef]=0.04, for a spectral bin that is opposed to the wind
    direction, the wind input factor W(k, θ) is negative, and its magnitude is 4% of
    the corresponding value of the spectral bin that is in the opposite direction
    (i.e. in the wind direction). See Zieger et al. (2015) eq. 11, where a0 is their
    notation for [rdcoef]. Default [rdcoef]=0.0 and `rdcoef=0.04` is recommended,
    though as implied by Zieger et al. (2015), this value is not well-established, so
    the user is encouraged to experiment with other values.

    References
    ----------
    Zieger, S., A.V. Babanin, W. E. Rogers and I.R. Young, 2015: Observation-based
    source terms in the third-generation wave model WAVEWATCH, Ocean Model., 96, 2-25.

    """

    model_type: Literal["negatinp"] = Field(
        default="negatinp", description="Model type discriminator"
    )
    rdcoef: confloat(ge=0.0, le=1.0) = Field(
        default=0.0,
        description="Coefficient representing the strength of negative wind input",
    )

    def cmd(self):
        return f"NEGATINP rdcoef={self.rdcoef}"


#======================================================================================
# SSWELL
#======================================================================================
class SSWELL(BaseSubComponent):
    """Swell dissipation sub-component.

    `SSWELL`

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

    def cmd(self):
        return "SSWELL"


class ROGERS(SSWELL):
    """Nonbreaking dissipation of Rogers et al. (2012).

    References
    ----------
    Rogers, W.E., A.V. Babanin and D.W. Wang, 2012: Observation-Consistent Input and
    Whitecapping Dissipation in a Model for Wind-Generated Surface Waves: Description
    and Simple Calculations, J. Atmos. Oceanic Technol., 29:9, 1329-1346.

    """

    model_type: Literal["rogers"] = Field(
        default="rogers", description="Model type discriminator"
    )
    cdsv: Optional[float] = Field(
        description="Coefficient related to laminar atmospheric boundary layer (SWAN default: 1.2)"
    )
    feswell: Optional[float] = Field(
        description="Swell dissipation factor"
    )

    def cmd(self):
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
    Ardhuin, F., A. Rogers, A. Babanin, J. Filipot, J. Magne, A. Roland, and P. van
    der Westhuysen, 2010: Semiempirical dissipation source functions for ocean waves.
    Part I: Definition, calibration, and validation, J. Phys. Oceanogr., 40, 1917-1941.

    """

    model_type: Literal["ardhuin"] = Field(
        default="ardhuin", description="Model type discriminator"
    )
    cdsv: Optional[float] = Field(
        description="Coefficient related to laminar atmospheric boundary layer (SWAN default: 1.2)"
    )

    def cmd(self):
        repr = f"{super().cmd()} ARDHUIN"
        if self.cdsv is not None:
            repr += f" cdsv={self.cdsv}"
        return repr


class ZIEGER(SSWELL):
    """Nonbreaking dissipation of Young et al. (2013) updated by Zieger et al. (2015).

    References
    ----------
    Zieger, S., A.V. Babanin, W. E. Rogers and I.R. Young, 2015: Observation-based
    source terms in the third-generation wave model WAVEWATCH, Ocean Model., 96, 2-25.

    Young, I.R., A.V.Babanin and S. Zieger, 2013: The Decay Rate of Ocean Swell
    Observed by Altimeter, J. Phys. Oceanogr., 43, 3233-3233.

    """

    model_type: Literal["zieger"] = Field(
        default="zieger", description="Model type discriminator"
    )
    b1: Optional[float] = Field(
        description="Non-dimensional proportionality coefficient"
    )
    negatinp: NEGATINP = Field(
        default=NEGATINP(),
        description="Negative wind input specification",
    )

    def cmd(self):
        repr = f"{super().cmd()} ZIEGER"
        if self.b1 is not None:
            repr += f" b1={self.b1}"
        return repr


#======================================================================================
# WCAPPING
#======================================================================================
class WCAPKOMEN(KOMEN):
    """Komen whitecapping sub-component.

    `WCAPPING KOMEN [cds2] [stpm] [powst] [delta] [powk]`

    Notes
    -----
    The SWAN default for `delta` has been changed since version 40.91A. The setting
    `delta = 1` will improve the prediction of the wave energy at low frequencies, and
    hence the mean wave period. The original default was `delta = 0`, which corresponds
    to WAM Cycle 3. See the Scientific/Technical documentation for further details.

    """
    model_type: Literal["wcapkomen"] = Field(
        default="wcapkomen", description="Model type discriminator"
    )
    powst: Optional[float] = Field(
        description="Power of steepness normalized with the wave steepness of a Pierson-Moskowitz spectrum (SWAN default: 2)"
    )
    delta: Optional[float] = Field(
        description="Coefficient which determines the dependency of the whitecapping on wave number (SWAN default: 1)"
    )
    powk: Optional[float] = Field(
        description="power of wave number normalized with the mean wave number (SWAN default: 1)",
    )

    def cmd(self):
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


class WCAPAB(WESTHUYSEN):
    """Whitecapping according to Alves and Banner (2003).

    `WCAPPING AB [cds2] [br] [cds3]`

    References
    ----------
    Alves, J.H.G.M. and M.L. Banner, 2003: A unified formulation of the wave-action
    balance equation, J. Phys. Oceanogr., 33, 2343-2356.

    """
    model_type: Literal["wcapab"] = Field(
        default="wcapab", description="Model type discriminator"
    )
    current: bool = Field(
        default=False,
        description="Indicates that enhanced current-induced dissipation as proposed by Van der Westhuysen (2012) is to be added",
    )
    cds3: Optional[float] = Field(
        description="Proportionality coefficient (SWAN default: 0.8)"
    )

    def cmd(self):
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


#======================================================================================
# QUADRUPL
#======================================================================================
class QUADRUPL(BaseSubComponent):
    """Nonlinear quadruplet wave interactions subcomponent.

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
        default=2,
        description="Numerical procedures for integrating the quadruplets: 1 = semi-implicit per sweep, 2 = explicit per sweep, 3 = explicit per iteration, 8 = explicit per iteration, but with a more efficient implementation, 4 = multiple DIA, 51 = XNL (deep water transfer), 52 = XNL (deep water transfer with WAM depth scaling), 53  XNL (finite depth transfer)",
    )
    clambda: Optional[float] = Field(
        alias="lambda",
        description="Coefficient for quadruplet configuration in case of DIA (SWAN default: 0.25)",
    )
    cn14: Optional[float] = Field(
        description="Proportionality coefficient for quadruplet interactions in case of DIA (SWAN default: 3.0e7",
    )
    csh1: Optional[float] = Field(
        description="Coefficient for shallow water scaling in case of DIA (SWAN default: 5.5",
    )
    csh2: Optional[float] = Field(
        description="Coefficient for shallow water scaling in case of DIA (SWAN default: 0.833333",
    )
    csh3: Optional[float] = Field(
        description="Coefficient for shallow water scaling in case of DIA (SWAN default: -1.25",
    )

    def cmd(self):
        repr = f"QUADRUPL iquad={self.iquad}"
        if self.clambda is not None:
            repr += f" lambda={self.clambda}"
        if self.cn14 is not None:
            repr += f" Cn14={self.cn14}"
        if self.csh1 is not None:
            repr += f" Csh1={self.csh1}"
        if self.csh2 is not None:
            repr += f" Csh2={self.csh2}"
        if self.csh3 is not None:
            repr += f" Csh3={self.csh3}"
        return repr


#======================================================================================
# BREAKING
#======================================================================================
class BREAKING(BaseSubComponent):
    """Wave breaking subcomponent.

    `BREAKING`

    With this command the user can influence depth-induced wave breaking in shallow
    water. If this command is not used, SWAN will account for wave breaking anyhow
    (with default options and values). If the user wants to specifically ignore wave
    breaking, he should use the command: OFF BREAKING.

    """
    model_type: Literal["breaking"] = Field(
        default="breaking", description="Model type discriminator"
    )

    def cmd(self):
        return f"BREAKING"


class CONSTANT(BREAKING):
    """Constant wave breaking index subcomponent.

    `BREAKING CONSTANT [alpha] [gamma]`

    Indicates that a constant breaker index is to be used.

    """
    model_type: Literal["constant"] = Field(
        default="constant", description="Model type discriminator"
    )
    alpha: Optional[float] = Field(
        description="Proportionality coefficient of the rate of dissipation (SWAN default: 1.0)"
    )
    gamma: Optional[float] = Field(
        description="The breaker index, i.e. the ratio of maximum individual wave height over depth (SWAN default: 0.73)"
    )

    def cmd(self):
        repr = f"{super().cmd()} CONSTANT"
        if self.alpha is not None:
            repr += f" alpha={self.alpha}"
        if self.gamma is not None:
            repr += f" gamma={self.gamma}"
        return repr


class BKD(BREAKING):
    """Variable wave breaking index subcomponent.

    `BREAKING BKD [alpha] [gamma0] [a1] [a2] [a3]`

    Indicates that the breaker index scales with both the bottom slope ($beta$) and the
    dimensionless depth (kd).

    """
    model_type: Literal["bkd"] = Field(
        default="bkd", description="Model type discriminator"
    )
    alpha: Optional[float] = Field(
        description="Proportionality coefficient of the rate of dissipation (SWAN default: 1.0)"
    )
    gamma0: Optional[float] = Field(
        description="The reference $gamma$ for horizontal slopes (SWAN default: 0.54)"
    )
    a1: Optional[float] = Field(
        description="First tunable coefficient for the breaker index (SWAN default: 7.59)"
    )
    a2: Optional[float] = Field(
        description="Second tunable coefficient for the breaker index (SWAN default: -8.06)"
    )
    a3: Optional[float] = Field(
        description="Third tunable coefficient for the breaker index (SWAN default: 8.09)"
    )

    def cmd(self):
        repr = f"{super().cmd()} BKD"
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


#======================================================================================
# FRICTION
#======================================================================================
class FRICTION(BaseSubComponent):
    """Wave bottom friction subcomponent.

    `FRICITON`

    With this optional command the user can activate bottom friction. If this command
    is not used, SWAN will not account for bottom friction. In SWAN four different
    formulations are available, i.e., that of Hasselmann et al. (1973, JONSWAP),
    Collins (1972), Madsen et al. (1988) and Smith et al. (2011). The default option
    is: JONSWAP with a constant friction coefficient. The recommended value for typical
    sandy bottoms is 0.038 m2s-3. Note that this value is to be applied for both wind
    sea and swell conditions. (The use of the previous default value of 0.067 m2s-3 is
    discouraged, even for wind sea conditions!) For smoother seafloors, like the Gulf
    of Mexico, a lower value of 0.019 m2s-3 is advised.

    """
    model_type: Literal["friction"] = Field(
        default="friction", description="Model type discriminator"
    )

    def cmd(self):
        return f"FRICTION"


class JONSWAP(FRICTION):
    """Jonswap friction subcomponent.

    `FRICTION JONSWAP CONSTANT [cfjon]`

    Indicates that the semi-empirical expression derived from the JONSWAP results for
    bottom friction dissipation (Hasselmann et al., 1973, JONSWAP) should be activated.
    This option is default.

    References
    ----------
    Hasselmann, K., Barnett, T.P., Bouws, E., Carlson, H., Cartwright, D.E., Enke, K.,
    Ewing, J.A., Gienapp, H., Hasselmann, D.E., Kruseman, P., Meerburg, A., Müller, P.,
    Olbers, D.J., Richter, K., Sell, W., Walden, H., 1973. Measurements of wind-wave
    growth and swell decay during the Joint North Sea Wave Project (JONSWAP). Deutches
    Hydrographisches Institut, Hamburg, Germany, Rep. No. 12, 95 pp.

    """
    model_type: Literal["jonswap"] = Field(
        default="jonswap", description="Model type discriminator"
    )
    cfjon: Optional[float] = Field(
        description="Coefficient of the JONSWAP formulation (SWAN default: 0.038)"
    )

    def cmd(self):
        repr = f"{super().cmd()} JONSWAP CONSTANT"
        if self.cfjon is not None:
            repr += f" cfjon={self.cfjon}"
        return repr


class COLLINS(FRICTION):
    """Collins (1972) friction subcomponent.

    `FRICTION COLLINS [cfw]`

    Note that `cfw` is allowed to vary over the computational region; in that case use
    the commands INPGRID FRICTION and READINP FRICTION to define and read the friction
    data. This command FRICTION is still required to define the type of friction
    expression. The value of `cfw` in this command is then not required (it will be
    ignored).

    References
    ----------
    Collins, M.B., 1972. The effect of bottom friction on the propagation of long
    waves. Coastal Engineering, 1972, 1, 163-181.

    """
    model_type: Literal["collins"] = Field(
        default="collins", description="Model type discriminator"
    )
    cfw: Optional[float] = Field(
        description="Collins bottom friction coefficient (SWAN default: 0.015)"
    )

    def cmd(self):
        repr = f"{super().cmd()} COLLINS"
        if self.cfw is not None:
            repr += f" cfw={self.cfw}"
        return repr


class MADSEN(FRICTION):
    """Madsen et al (1988) friction subcomponent.

    `FRICTION MADSEN [kn]`

    Note that `kn` is allowed to vary over the computational region; in that case use
    the commands INPGRID FRICTION and READINP FRICTION to define and read the friction
    data. This command FRICTION is still required to define the type of friction
    expression. The value of `kn` in this command is then not required (it will be
    ignored).

    References
    ----------
    Madsen, O.S., Sørensen, O.R., Schäffer, H.A., 1988. Surf zone dynamics simulated by
    a Boussinesq type model. Part I. Model description and cross-shore motion of
    regular waves. Coastal Engineering, 1988, 12, 115-145.

    """
    model_type: Literal["madsen"] = Field(
        default="madsen", description="Model type discriminator"
    )
    kn: Optional[float] = Field(
        description="equivalent roughness length scale of the bottom (in m) (SWAN default: 0.05)"
    )
#======================================================================================
# FRICTION
#======================================================================================class RIPPLES(FRICTION):
    """Ripples friction subcomponent.

    `FRICTION RIPPLES [S] [D]`

    Indicates that the expression of Smith et al. (2011) should be activated. Here
    friction depends on the formation of bottom ripples and sediment size.

    References
    ----------
    Smith, J.M., McCall, R.T., 2011. A model for wave dissipation in the surf zone
    based on field observations. Coastal Engineering, 2011, 58, 917-928.

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

    def cmd(self):
        repr = f"{super().cmd()} RIPPLES"
        if self.s is not None:
            repr += f" S={self.s}"
        if self.d is not None:
            repr += f" D={self.d}"
        return repr


#======================================================================================
# TRIAD
#======================================================================================
class TRIAD(BaseSubComponent):
    """Wave triads subcomponent.

    `TRIAD`

    With this command the user can activate the triad wave-wave interactions. If this
    command is not used, SWAN will not account for triads.

    """
    model_type: Literal["triad"] = Field(
        default="triad", description="Model type discriminator"
    )
    def cmd(self):
        return f"TRIAD"


#======================================================================================
# VEGETATION
#======================================================================================
class VEGETATION(BaseSubComponent):
    """Vegetation subcomponent.

    `VEGETATION`

    With this command the user can activate wave damping due to vegetation based on the
    Dalrymple's formula (1984) as implemented by Suzuki et al. (2011). This damping is
    uniform over the wave frequencies. An alternative is the frequency-dependent
    (canopy) dissipation model of Jacobsen et al. (2019). If this command is not used,
    SWAN will not account for vegetation effects.

    References
    ----------
    Dalrymple, R.A., 1984. Water wave interactions with vegetation: Part 1. A fully
    nonlinear theory. Journal of Fluid Mechanics, 1984, 140, 197-229.

    """
    model_type: Literal["vegetation"] = Field(
        default="vegetation", description="Model type discriminator"
    )
    def cmd(self):
        return f"VEGETATION"


#======================================================================================
# MUD
#======================================================================================
class MUD(BaseSubComponent):
    """Mud subcomponent.

    `MUD`

    With this command the user can activate wave damping due to mud based on Ng (2000).
    If this command or the commands INPGRID MUDLAY and READINP MUDLAY are not used,
    SWAN will not account for muddy bottom effects.

    References
    ----------
    Ng, C.O., 2000. Wave attenuation in mudflat and salt marsh vegetation. Journal of
    Coastal Research, 2000, 16, 379-389.

    """
    model_type: Literal["mud"] = Field(
        default="mud", description="Model type discriminator"
    )
    def cmd(self):
        return f"MUD"


#======================================================================================
# SICE
#======================================================================================
class SICE(BaseSubComponent):
    """Sea ice subcomponent.

    `SICE`

    Using this command, the user activates a sink term to represent the dissipation of
    wave energy by sea ice. The R19 method is empirical/parametric: a polynomial based
    on wave frequency (Rogers, 2019). This polynomial (in 1/m) has seven dimensional
    coefficients; see Scientific/Technical documentation for details. If this command
    is not used, SWAN will not account for sea ice effects.

    References
    ----------
    Doble, M.J., Bidlot, J.R., Wadhams, P., 2015. Sea ice and ocean wave modelling in
    the Arctic: Interactions between waves and ice in a coupled atmosphere-wave-ice
    model. Ocean Modelling, 2015, 96, 141-155.

    Meylan, M.H., Bennetts, L.G., Thomas, T., 2014. Dissipation of ocean waves by sea
    ice. Geophysical Research Letters, 2014, 41, 7561-7568.

    Meylan, M.H., Bennetts, L.G., Williams, T.D., 2018. Wave attenuation by pancake
    ice. Journal of Geophysical Research: Oceans, 2018, 123, 1-16.

    Rogers, W.E., 2019. Wave attenuation by sea ice: A new parametric model. Journal of
    Geophysical Research: Oceans, 2019, 124, 1-15.

    """
    model_type: Literal["sice"] = Field(
        default="sice", description="Model type discriminator"
    )
    def cmd(self):
        return f"SICE"


#======================================================================================
# TURBULENCE
#======================================================================================
class TURBULENCE(BaseSubComponent):
    """Turbulence subcomponent.

    `TURBULENCE`

    With this optional command the user can activate turbulent viscosity. This physical
    effect is also activated by reading values of the turbulent viscosity using the
    `READGRID TURB` command, but then with the default value of `ctb`. The command
    `READGRID TURB` is necessary if this command `TURB` is used since the value of the
    viscosity is assumed to vary over space.

    """
    model_type: Literal["turbulence"] = Field(
        default="turbulence", description="Model type discriminator"
    )
    def cmd(self):
        return f"TURBULENCE"


#======================================================================================
# BRAGG
#======================================================================================
class BRAGG(BaseSubComponent):
    """Bragg scattering subcomponent.

    `BRAGG`

    Using this optional command, the user activates a source term to represent the
    scattering of waves due to changes in the small-scale bathymetry based on the
    theory of Ardhuin and Herbers (2002). If this command is not used, SWAN will not
    account for Bragg scattering.

    """
    model_type: Literal["bragg"] = Field(
        default="bragg", description="Model type discriminator"
    )
    def cmd(self):
        return f"BRAGG"


#======================================================================================
# LIMITER
#======================================================================================
class LIMITER(BaseSubComponent):
    """Limiter subcomponent.

    `LIMITER`

    With this command the user can de-activate permanently the quadruplets when
    the actual Ursell number exceeds `ursell`. Moreover, as soon as the actual
    fraction of breaking waves exceeds [qb] then the action limiter will not be
    used in case of decreasing action density.

    """
    model_type: Literal["limiter"] = Field(
        default="limiter", description="Model type discriminator"
    )
    def cmd(self):
        return f"LIMITER"


#======================================================================================
# OBSTACLE
#======================================================================================
class OBSTACLE(BaseSubComponent):
    """Obstacle subcomponent.

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
    def cmd(self):
        return f"OBSTACLE"

#======================================================================================
# OBSTACLE FIG
#======================================================================================
class OBSTACLE_FIG(BaseSubComponent):
    """Obstacle figure subcomponent.

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
    def cmd(self):
        return f"OBSTACLE FIG"


#======================================================================================
# SETUP
#======================================================================================
class SETUP(BaseSubComponent):
    """Setup subcomponent.

    `SETUP`

    """
    model_type: Literal["setup"] = Field(
        default="setup", description="Model type discriminator"
    )
    def cmd(self):
        return f"SETUP"

#======================================================================================
# DIFFRACTION
#======================================================================================
class DIFFRACTION(BaseSubComponent):
    """Wave diffraction subcomponent.

    `DIFFRACTION`

    """
    model_type: Literal["diffraction"] = Field(
        default="diffraction", description="Model type discriminator"
    )
    def cmd(self):
        return f"DIFFRACTION"


#======================================================================================
# SURFBEAT
#======================================================================================
class SURFBEAT(BaseSubComponent):
    """Surfbeat subcomponent.

    `SURFBEAT`

    """
    model_type: Literal["surfbeat"] = Field(
        default="surfbeat", description="Model type discriminator"
    )
    def cmd(self):
        return f"SURFBEAT"


#======================================================================================
# SCAT
#======================================================================================
class SCAT(BaseSubComponent):
    """Scattering subcomponent.

    `SCAT`

    """
    model_type: Literal["scat"] = Field(
        default="scat", description="Model type discriminator"
    )
    def cmd(self):
        return f"SCAT"
