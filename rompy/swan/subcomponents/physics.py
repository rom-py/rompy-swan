"""SWAN physics subcomponents."""
from typing import Literal, Optional
from pydantic import Field, validator, root_validator, confloat
from abc import ABC
from pydantic_numpy import NDArray
import numpy as np

from rompy.swan.subcomponents.base import BaseSubComponent


JSON_ENCODERS = {np.ndarray: lambda arr: arr.tolist()}


# ======================================================================================
# Source terms
# ======================================================================================
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
        description=(
            "Proportionality coefficient when activating the Cavaleri and Malanotte "
            "(1981) wave growth term"
        ),
    )


class JANSSEN(SourceTerms):
    """Janssen source terms subcomponent.

    `JANSSEN [cds1] [delta]`

    References
    ----------
    Janssen, P.A., 1989. Wave-induced stress and the drag of air flow over sea waves.
    Journal of Physical Oceanography, 19(6), pp.745-754.

    Janssen, P.A.E.M., Lionello, P. and Zambresky, L., 1989. On the interaction of wind
    and waves. Philosophical transactions of the royal society of London. Series A,
    Mathematical and Physical Sciences, 329(1604), pp.289-301.

    Janssen, P.A., 1991. Quasi-linear theory of wind-wave generation applied to wave
    forecasting. Journal of physical oceanography, 21(11), pp.1631-1642.

    """

    model_type: Literal["janssen"] = Field(
        default="janssen", description="Model type discriminator"
    )
    cds1: Optional[float] = Field(
        description=(
            "Coefficient for determining the rate of whitecapping dissipation "
            "($Cds / s^4_{PM}$) (SWAN default: 4.5)"
        ),
    )
    delta: Optional[float] = Field(
        description=(
            "Coefficient which determines the dependency of the whitecapping on wave "
            "number (mix with Komen et al. formulation) (SWAN default: 0.5)"
        ),
    )

    def cmd(self) -> str:
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
    Komen, G.J., Hasselmann, S. and Hasselmann, K., 1984. On the existence of a fully
    developed wind-sea spectrum. Journal of physical oceanography, 14(8), pp.1271-1285.

    """

    model_type: Literal["komen"] = Field(
        default="komen", description="Model type discriminator"
    )
    cds2: Optional[float] = Field(
        description=(
            "Coefficient for determining the rate of whitecapping dissipation "
            "(`Cds`) (SWAN default: 2.36e-5)"
        ),
    )
    stpm: Optional[float] = Field(
        description=(
            "Value of the wave steepness for a Pierson-Moskowitz spectrum "
            "(`s^2_PM`) (SWAN default: 3.02e-3)"
        ),
    )

    def cmd(self) -> str:
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
    van der Westhuysen, A.J., Zijlema, M. and Battjes, J.A., 2007. Nonlinear
    saturation-based whitecapping dissipation in SWAN for deep and shallow water.
    Coastal Engineering, 54(2), pp.151-170.

    """

    model_type: Literal["westhuysen"] = Field(
        default="westhuysen", description="Model type discriminator"
    )
    cds2: Optional[float] = Field(
        description=(
            "proportionality coefficient due to Alves and Banner (2003) "
            "(SWAN default: 5.0e-5)."
        ),
    )
    br: Optional[float] = Field(
        description="Threshold saturation level	(SWAN default: 1.75e-3)"
    )

    def cmd(self) -> str:
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
    Fan, Y., Lin, S.J., Held, I.M., Yu, Z. and Tolman, H.L., 2012. Global ocean surface
    wave simulation using a coupled atmosphere–wave model. Journal of Climate, 25(18),
    pp.6233-6252.

    Rogers, W.E., Babanin, A.V. and Wang, D.W., 2012. Observation-consistent input and
    whitecapping dissipation in a model for wind-generated surface waves: Description
    and simple calculations. Journal of Atmospheric and Oceanic Technology, 29(9),
    pp.1329-1346.

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
        description=(
            "Power coefficient controlling strength of dissipation term T1 "
            "(L in RBW12, SWAN default: 4)"
        ),
    )
    p2sds: Optional[float] = Field(
        description=(
            "Power coefficient controlling strength of dissipation term T2 "
            "(M in RBW12, SWAN default: 4)"
        ),
    )
    normalization: Literal["up", "down"] = Field(
        default="up",
        description=(
            "Selection of normalization of exceedance level by ET(f) (`up`) or E(f) "
            "(`down`) as in RBW12 (right column, page 1333), `up` is default and "
            "strongly recommended"
        ),
    )
    wind_drag: Literal["hwang", "fan", "ecmwf"] = Field(
        default="hwang",
        description=(
            "Wind drag formula, `hwang` is the default and is unchanged from RBW12, "
            "`fan` is from Fan et al. (2012), `ecmwf` follows WAM Cycle 4 methodology"
        ),
    )
    tau: Literal["vectau", "scatau"] = Field(
        default="vectau",
        description=(
            "Use vector (vectau) or scalar (scatau) calculation for the wind strerss "
            "(Eq. 12 in RBW12), `vectau` is the default and strongly recommended"
        ),
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
        description=(
            "Counter bias in the input wind fields by providing a multiplier "
            "on the drag coefficient"
        ),
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
    def u10_cmd(self) -> str:
        if self.u10 == "true10":
            return "TRUE10"
        else:
            return f"U10PROXY windscaling={self.windscaling}"

    def cmd(self) -> str:
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
    """Fourth ST6 calibration settings defined in the SWAN user manual."""

    model_type: Literal["st6c4"] = Field(default="st6c4")
    cdfac: Literal[0.89] = Field(default=0.89)


class ST6C5(ST6C1):
    """Fifth ST6 calibration settings defined in the SWAN user manual."""

    model_type: Literal["st6c5"] = Field(default="st6c5")
    cdfac: Literal[0.89] = Field(default=0.89)
    a1sds: Literal[6.5e-6] = Field(default=6.5e-6)
    a2sds: Literal[8.5e-5] = Field(default=8.5e-5)
    windscaling: Literal[35.0] = Field(default=35.0)


# =====================================================================================
# Triads
# =====================================================================================
class ELDEBERKY(BaseSubComponent):
    """Biphase parameterization as a funtion of the Ursell number of Eldeberky (1999).

    `BIPHASE ELDEBERKY [urcrit]`

    References
    ----------
    Eldeberky, Y., Polnikov, V. and Battjes, J.A., 1996. A statistical approach for
    modeling triad interactions in dispersive waves. In Coastal Engineering 1996
    (pp. 1088-1101).

    Eldeberky, Y. and Madsen, P.A., 1999. Deterministic and stochastic evolution
    equations for fully dispersive and weakly nonlinear waves. Coastal Engineering,
    38(1), pp.1-24.

    Doering, J.C. and Bowen, A.J., 1995. Parametrization of orbital velocity
    asymmetries of shoaling and breaking waves using bispectral analysis. Coastal
    engineering, 26(1-2), pp.15-33.

    """

    model_type: Literal["eldeberky"] = Field(
        default="eldeberky", description="Model type discriminator"
    )
    urcrit: Optional[float] = Field(
        description=(
            "The critical Ursell number appearing in the parametrization. Note: the "
            "value of `urcrit` is setted by Eldeberky (1996) at 0.2 based on a "
            "laboratory experiment, whereas Doering and Bowen (1995) employed the "
            "value of 0.63 based on the field experiment data (SWAN default: 0.63)"
        )
    )

    def cmd(self) -> str:
        repr = "BIPHASE ELDEBERKY"
        if self.urcrit is not None:
            repr += f" urcrit={self.urcrit}"
        return repr


class DEWIT(BaseSubComponent):
    """Biphase parameterization based on bed slope and peak period of De Wit (2022).

    `BIPHASE DEWIT [lpar]`

    References
    ----------
    De Wit, F.P., 2022. Wave shape prediction in complex coastal systems (Doctoral
    dissertation, PhD. thesis. Delft University of Technology. https://repository.
    tudelft. nl/islandora/object/uuid% 3A0fb850a4-4294-4181-9d74-857de21265c2).

    """

    model_type: Literal["dewit"] = Field(
        default="dewit", description="Model type discriminator"
    )
    lpar: Optional[float] = Field(
        description=(
            "Scales spatial averaging of the De Wit's biphase in terms of a multiple "
            "of peak wave length of the incident wave field. Note: `lpar` = 0` means "
            "no averaging (SWAN default: 0)"
        )
    )

    def cmd(self) -> str:
        repr = "BIPHASE DEWIT"
        if self.lpar is not None:
            repr += f" lpar={self.lpar}"
        return repr


# =====================================================================================
# Transmission
# =====================================================================================
class TRANSM(BaseSubComponent):
    """Constant transmission coefficient.

    `TRANSM [trcoef]`

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.subcomponents.physics import TRANSM
        transm = TRANSM(trcoef=0.5)
        print(transm.render())

    """

    model_type: Literal["transm", "TRANSM"] = Field(
        default="transm", description="Model type discriminator"
    )
    trcoef: Optional[float] = Field(
        description=(
            "Constant transmission coefficient (ratio of transmitted over incoming "
            "significant wave height) (SWAN default: 0.0) (no transmission = complete "
            "blockage)"
        ),
        ge=0.0,
        le=1.0,
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "TRANSM"
        if self.trcoef is not None:
            repr += f" trcoef={self.trcoef}"
        return repr


class TRANS1D(BaseSubComponent):
    """Frequency dependent transmission coefficient.

    `TRANS1D < [trcoef] >`

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        @suppress
        from rompy.swan.subcomponents.physics import TRANS1D

        transm = TRANS1D(trcoef=[0.0, 0.0, 0.2, 0.5, 0.2, 0.0, 0.0])
        print(transm.render())

    """

    model_type: Literal["trans1d", "TRANS1D"] = Field(
        default="trans1d", description="Model type discriminator"
    )
    trcoef: list[float] = Field(
        description=(
            "Transmission coefficient (ratio of transmitted over incoming significant "
            "wave height) per frequency. The number of these transmission values must "
            "be equal to the number of frequencies, i.e. `msc` + 1"
        ),
        ge=0.0,
        le=1.0,
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        return f"TRANS1D {' '.join(str(v) for v in self.trcoef)}"


class TRANS2D(BaseSubComponent):
    """Frequency-direction dependent transmission coefficient.

    `TRANS2D < [trcoef] >`

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        @suppress
        from rompy.swan.subcomponents.physics import TRANS2D

        trcoef = np.array([[0.0, 0.0], [0.1, 0.1], [0.2, 0.2]])
        transm = TRANS2D(trcoef=trcoef)
        print(transm.render())

    """

    model_type: Literal["trans2d", "TRANS2D"] = Field(
        default="trans2d", description="Model type discriminator"
    )
    trcoef: NDArray = Field(
        description=(
            "Transmission coefficient (ratio of transmitted over incoming significant "
            "wave height) per frequency and direction, rows represent directions and "
            "columns represent frequencies"
        ),
    )

    class Config:
        json_encoders = JSON_ENCODERS

    @validator("trcoef")
    def constrained_0_1(cls, value):
        """Ensure all directions have the same number of frequencies."""
        if value.min() < 0 or value.max() > 1:
            raise ValueError("Transmission coefficients must be between 0.0 and 1.0")
        return value

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "TRANS2D"
        for coef in self.trcoef:
            repr += f" &\n\t{' '.join(str(v) for v in coef)}"
        return f"{repr} &\n\t"
