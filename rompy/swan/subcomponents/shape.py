"""Spectral shape subcomponents."""
import logging
from typing import Literal
from abc import ABC
from pydantic import confloat

from rompy.swan.subcomponents.base import BaseSubComponent


logger = logging.getLogger(__name__)


class JONSWAP(BaseSubComponent):
    """Jonswap spectral shape.

    `JONSWAP [gamma]`

    parameters
    ----------
    model_type: Literal["jonswap"]
        Model type discriminator.
    gamma: float
        Peak enhancement parameter of the JONSWAP spectrum.

    """

    model_type: Literal["jonswap"] = "jonswap"
    gamma: confloat(gt=0.0) = 3.3

    def cmd(self) -> str:
        return f"{super().cmd()} gamma={self.gamma}"


class TMA(JONSWAP):
    """TMA spectral shape.

    `TMA [gamma] [d]`

    parameters
    ----------
    model_type: Literal["tma"]
        Model type discriminator.
    gamma: float
        Peak enhancement parameter of the JONSWAP spectrum.
    d: float
        The reference depth at the wave maker in meters.

    """

    model_type: Literal["tma"] = "tma"
    d: confloat(gt=0.0)

    def cmd(self) -> str:
        return f"{super().cmd()} d={self.d}"


class GAUSS(BaseSubComponent):
    """Gaussian spectral shape.

    `GAUSS [sigfr]`

    parameters
    ----------
    model_type: Literal["gauss"]
        Model type discriminator.
    sigfr: float
        Width of the Gaussian frequency spectrum expressed as a standard deviation in Hz.

    """

    model_type: Literal["gauss"] = "gauss"
    sigfr: confloat(gt=0.0)

    def cmd(self) -> str:
        return f"{super().cmd()} sigfr={self.sigfr}"


class PM(BaseSubComponent):
    """Pearson-Moskowitz spectral shape.

    `PM`

    parameters
    ----------
    model_type: Literal["pm"]
        Model type discriminator.

    """

    model_type: Literal["pm"] = "pm"


class BIN(BaseSubComponent):
    """Single frequency bin spectral shape.

    `BIN`

    parameters
    ----------
    model_type: Literal["bin"]
        Model type discriminator.

    """

    model_type: Literal["bin"] = "bin"


class SHAPESPEC(BaseSubComponent):
    """SWAN BOUND SHAPESPEC subcomponent.

    `BOUND SHAPESPEC JONSWAP|PM|GAUSS|BIN|TMA PEAK|MEAN DSPR [POWER|DEGREES]`

    This command BOUND SHAPESPEC defines the shape of the spectra (both in frequency
    and direction) at the boundary of the computational grid in case of parametric
    spectral input.

    Parameters
    ----------
    model_type: Literal["shapespec"]
        Model type discriminator.
    shape: JONSWAP | PM | GAUSS | BIN | TMA
        The spectral shape.
    per_type: Literal['peak', 'mean']
        The type of characteristic wave period
    dspr_type: Literal['power', 'degrees']

    """

    model_type: Literal["shapespec"] = "shapespec"
    shape: JONSWAP | PM | GAUSS | BIN | TMA = JONSWAP()
    per_type: Literal["peak", "mean"] = "peak"
    dspr_type: Literal["power", "degrees"] = "power"

    def cmd(self) -> str:
        repr = (
            f"BOUND SHAPESPEC {self.shape.render()} {self.per_type.upper()} "
            f"DSPR {self.dspr_type.upper()}"
        )
        return repr
