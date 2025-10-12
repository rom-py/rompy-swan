"""SWAN sea ice components.

This module contains components for configuring wave dissipation by sea ice in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class SICE(BaseComponent):
    """Sea ice dissipation.

    .. code-block:: text

        SICE [aice]

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
    the ONR "Sea State" field experiment. Nav. Res. Lab. Memo. Rep, pp.18-9801.

    Rogers, W.E., Meylan, M.H. and Kohout, A.L., 2021. Estimates of spectral wave
    attenuation in Antarctic sea ice, using model/data inversion. Cold Regions Science
    and Technology, 182, p.103198.

    Notes
    -----
    Iis also necessary to describe the ice, using the `ICE` command (for uniform and
    stationary ice) or `INPGRID`/`READINP` commands (for variable ice).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import SICE
        sice = SICE()
        print(sice.render())
        sice = SICE(aice=0.5)
        print(sice.render())

    TODO: Verify if the `aice` parameter should be used with SICE command, it is not
    shown in the command tree but it is described as an option in the description.

    """

    model_type: Literal["sice", "SICE"] = Field(
        default="sice", description="Model type discriminator"
    )
    aice: Optional[float] = Field(
        default=None,
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
        """Command file string for this component."""
        repr = "SICE"
        if self.aice is not None:
            repr += f" aice={self.aice}"
        return repr


class R19(SICE):
    """Sea ice dissipation based on the method of Rogers et al (2019).

    .. code-block:: text

        SICE [aice] R19 [c0] [c1] [c2] [c3] [c4] [c5] [c6]

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
    the ONR "Sea State" field experiment. Nav. Res. Lab. Memo. Rep, pp.18-9801.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics.sice import R19
        sice = R19()
        print(sice.render())
        kwargs = dict(
            aice=0.5,
            c0=0.0,
            c1=0.0,
            c2=1.06e-3,
            c3=0.0,
            c4=0.0,
            c5=0.0,
            c6=0.0,
        )
        sice = R19(**kwargs)
        print(sice.render())

    """

    model_type: Literal["r19", "R19"] = Field(
        default="r19", description="Model type discriminator"
    )
    c0: Optional[float] = Field(
        default=None,
        description=(
            "Polynomial coefficient (in 1/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )
    c1: Optional[float] = Field(
        default=None,
        description=(
            "Polynomial coefficient (in s/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )
    c2: Optional[float] = Field(
        default=None,
        description=(
            "Polynomial coefficient (in s2/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 1.06E-3)"
        ),
    )
    c3: Optional[float] = Field(
        default=None,
        description=(
            "Polynomial coefficient (in s3/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )
    c4: Optional[float] = Field(
        default=None,
        description=(
            "Polynomial coefficient (in s4/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 2.3E-2)"
        ),
    )
    c5: Optional[float] = Field(
        default=None,
        description=(
            "Polynomial coefficient (in s5/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )
    c6: Optional[float] = Field(
        default=None,
        description=(
            "Polynomial coefficient (in s6/m) for determining the rate of sea ice "
            "dissipation (SWAN default: 0.0)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
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

    .. code-block:: text

        SICE [aice] D15 [chf]

    References
    ----------
    Doble, M.J., De Carolis, G., Meylan, M.H., Bidlot, J.R. and Wadhams, P., 2015.
    Relating wave attenuation to pancake ice thickness, using field measurements and
    model results. Geophysical Research Letters, 42(11), pp.4473-4481.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics.sice import D15
        sice = D15()
        print(sice.render())
        sice = D15(aice=0.2, chf=0.1)
        print(sice.render())

    """

    model_type: Literal["d15", "D15"] = Field(
        default="d15", description="Model type discriminator"
    )
    chf: Optional[float] = Field(
        default=None,
        description="A simple coefficient of proportionality (SWAN default: 0.1)",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"{super().cmd()} {self.model_type.upper()}"
        if self.chf is not None:
            repr += f" chf={self.chf}"
        return repr


class M18(SICE):
    """Sea ice dissipation based on the method of Meylan et al. (2018).

    .. code-block:: text

        SICE [aice] M18 [chf]

    References
    ----------
    Meylan, M.H., Bennetts, L.G. and Kohout, A.L., 2014. In situ measurements and
    analysis of ocean waves in the Antarctic marginal ice zone. Geophysical Research
    Letters, 41(14), pp.5046-5051.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics.sice import M18
        sice = M18()
        print(sice.render())
        sice = M18(aice=0.8, chf=0.059)
        print(sice.render())

    """

    model_type: Literal["m18", "M18"] = Field(
        default="m18", description="Model type discriminator"
    )
    chf: Optional[float] = Field(
        default=None,
        description="A simple coefficient of proportionality (SWAN default: 0.059)",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"{super().cmd()} {self.model_type.upper()}"
        if self.chf is not None:
            repr += f" chf={self.chf}"
        return repr


class R21B(SICE):
    """Sea ice dissipation based on the method of Rogers et al. (2021).

    .. code-block:: text

        SICE [aice] R21B [chf] [npf]

    References
    ----------
    Rogers, W.E., Meylan, M.H. and Kohout, A.L., 2021. Estimates of spectral wave
    attenuation in Antarctic sea ice, using model/data inversion. Cold Regions Science
    and Technology, 182, p.103198.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics.sice import R21B
        sice = R21B()
        print(sice.render())
        sice = R21B(aice=0.8, chf=2.9, npf=4.5)
        print(sice.render())

    """

    model_type: Literal["r21b", "R21B"] = Field(
        default="r21b", description="Model type discriminator"
    )
    chf: Optional[float] = Field(
        default=None,
        description="A simple coefficient of proportionality (SWAN default: 2.9)",
    )
    npf: Optional[float] = Field(
        default=None,
        description=(
            "Controls the degree of dependence on frequency and ice thickness "
            "(SWAN default: 4.5)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"{super().cmd()} {self.model_type.upper()}"
        if self.chf is not None:
            repr += f" chf={self.chf}"
        if self.npf is not None:
            repr += f" npf={self.npf}"
        return repr
