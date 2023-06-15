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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
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
    def cmd(self) -> str:
        return f"SCAT"
