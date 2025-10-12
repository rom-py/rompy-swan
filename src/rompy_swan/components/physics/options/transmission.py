"""SWAN transmission models for OBSTACLE components.

This module contains all models used for wave transmission through obstacles:
- TRANSM: Constant transmission coefficient
- TRANS1D: Frequency dependent transmission
- TRANS2D: Frequency-direction dependent transmission
These are private implementation details used as field types in OBSTACLE components.
"""

from typing import Annotated, Literal, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_numpy.typing import Np2DArray

from rompy_swan.subcomponents.base import BaseSubComponent


class TRANSM(BaseSubComponent):
    """Constant transmission coefficient.
    .. code-block:: text

        TRANSM [trcoef]

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._transmission import TRANSM
        transm = TRANSM()
        print(transm.render())
        transm = TRANSM(trcoef=0.5)
        print(transm.render())

    """

    model_type: Literal["transm", "TRANSM"] = Field(
        default="transm", description="Model type discriminator"
    )
    trcoef: Optional[float] = Field(
        default=None,
        description=(
            "Constant transmission coefficient (ratio of transmitted over incoming "
            "significant wave height) (SWAN default: 0.0) (no transmission = complete "
            "blockage)"
        ),
        ge=0.0,
        le=1.0,
    )

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        repr = "TRANSM"
        if self.trcoef is not None:
            repr += f" trcoef={self.trcoef}"
        return repr


class TRANS1D(BaseSubComponent):
    """Frequency dependent transmission.

    .. code-block:: text

        TRANS1D < [trcoef] >

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._transmission import TRANS1D
        transm = TRANS1D(trcoef=[0.0, 0.0, 0.2, 0.5, 0.2, 0.0, 0.0])
        print(transm.render())

    """

    model_type: Literal["trans1d", "TRANS1D"] = Field(
        default="trans1d", description="Model type discriminator"
    )
    trcoef: list[Annotated[float, Field(ge=0.0, le=1.0)]] = Field(
        description=(
            "Transmission coefficient (ratio of transmitted over incoming significant "
            "wave height) per frequency. The number of these transmission values must "
            "be equal to the number of frequencies, i.e. `msc` + 1"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        return f"TRANS1D {' '.join(str(v) for v in self.trcoef)}"


class TRANS2D(BaseSubComponent):
    """Frequency-direction dependent transmission.

    .. code-block:: text

        TRANS2D < [trcoef] >

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._transmission import TRANS2D
        import numpy as np
        trcoef = np.array([[0.0, 0.0], [0.1, 0.1], [0.2, 0.2]])
        transm = TRANS2D(trcoef=trcoef)
        print(transm.render())

    """

    model_type: Literal["trans2d", "TRANS2D"] = Field(
        default="trans2d", description="Model type discriminator"
    )
    trcoef: Np2DArray = Field(
        description=(
            "Transmission coefficient (ratio of transmitted over incoming significant "
            "wave height) per frequency and direction, rows represent directions and "
            "columns represent frequencies"
        ),
    )

    @field_validator("trcoef")
    @classmethod
    def constrained_0_1(cls, value: float) -> float:
        """Ensure all directions have the same number of frequencies."""
        if value.min() < 0 or value.max() > 1:
            raise ValueError("Transmission coefficients must be between 0.0 and 1.0")
        return value

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        repr = "TRANS2D"
        for coef in self.trcoef:
            repr += f" &\n\t{' '.join(str(v) for v in coef)}"
        return f"{repr} &\n\t"


class GODA(BaseSubComponent):
    """DAM transmission of Goda/Seelig (1979).

    .. code-block:: text

        DAM GODA [hgt] [alpha] [beta]

    This option specified transmission coefficients dependent on the incident wave
    conditions at the obstacle and on the obstacle height (which may be submerged).

    References
    ----------
    Goda, Y. and Suzuki, Y., 1976. Estimation of incident and reflected waves in random
    wave experiments. In Coastal Engineering 1976 (pp. 828-845).

    Seelig, W.N., 1979. Effects of breakwaters on waves: Laboratory test of wave
    transmission by overtopping. In Proc. Conf. Coastal Structures, 1979
    (Vol. 79, No. 2, pp. 941-961).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._transmission import GODA
        transm = GODA(hgt=3.0)
        print(transm.render())
        transm = GODA(hgt=3.0, alpha=2.6, beta=0.15)
        print(transm.render())

    """

    model_type: Literal["goda", "GODA"] = Field(
        default="goda", description="Model type discriminator"
    )
    hgt: float = Field(
        description=(
            "The elevation of the top of the obstacle above reference level (same "
            "reference level as for bottom etc.); use a negative value if the top is "
            "below that reference level"
        ),
    )
    alpha: Optional[float] = Field(
        default=None,
        description=(
            "coefficient determining the transmission coefficient for Goda's "
            "transmission formula (SWAN default: 2.6)"
        ),
    )
    beta: Optional[float] = Field(
        default=None,
        description=(
            "Another coefficient determining the transmission coefficient for Goda's "
            "transmission formula (SWAN default: 0.15)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        repr = f"DAM {self.model_type.upper()} hgt={self.hgt}"
        if self.alpha is not None:
            repr += f" alpha={self.alpha}"
        if self.beta is not None:
            repr += f" beta={self.beta}"
        return repr


class DANGREMOND(BaseSubComponent):
    """DAM transmission of d'Angremond et al. (1996).

    .. code-block:: text

        DAM DANGREMOND [hgt] [slope] [Bk]

    This option specifies transmission coefficients dependent on the incident wave
    conditions at the obstacle and on the obstacle height (which may be submerged).

    References
    ----------
    d'Angremond, K., Van Der Meer, J.W. and De Jong, R.J., 1996. Wave transmission at
    low-crested structures. In Coastal Engineering 1996 (pp. 2418-2427).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics._transmission import DANGREMOND
        transm = DANGREMOND(hgt=3.0, slope=60, Bk=10.0)
        print(transm.render())

    """

    model_type: Literal["dangremond", "DANGREMOND"] = Field(
        default="dangremond", description="Model type discriminator"
    )
    hgt: float = Field(
        description=(
            "The elevation of the top of the obstacle above reference level (same "
            "reference level as for bottom etc.); use a negative value if the top is "
            "below that reference level"
        ),
    )
    slope: float = Field(
        description="The slope of the obstacle (in degrees)", ge=0.0, le=90.0
    )
    Bk: float = Field(description="The crest width of the obstacle")

    def cmd(self) -> str:
        """Command file string for this subcomponent."""
        repr = f"DAM {self.model_type.upper()}"
        repr += f" hgt={self.hgt} slope={self.slope} Bk={self.Bk}"
        return repr
