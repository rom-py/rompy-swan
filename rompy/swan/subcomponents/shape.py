"""Spectral shape subcomponents."""
import logging
from typing import Literal
from abc import ABC
from pydantic import Field, confloat

from rompy.swan.subcomponents.base import BaseSubComponent


logger = logging.getLogger(__name__)


class JONSWAP(BaseSubComponent):
    """Jonswap spectral shape.

    `JONSWAP [gamma]`

    """

    model_type: Literal["jonswap"] = Field(
        default="jonswap", description="Model type discriminator"
    )
    gamma: confloat(gt=0.0) = Field(
        default=3.3,
        description="Peak enhancement parameter of the JONSWAP spectrum.",
    )

    def cmd(self) -> str:
        return f"{super().cmd()} gamma={self.gamma}"


class TMA(JONSWAP):
    """TMA spectral shape.

    `TMA [gamma] [d]`

    """

    model_type: Literal["tma"] = Field(
        default="tma", description="Model type discriminator"
    )
    d: confloat(gt=0.0) = Field(
        description="The reference depth at the wave maker in meters.",
    )

    def cmd(self) -> str:
        return f"{super().cmd()} d={self.d}"


class GAUSS(BaseSubComponent):
    """Gaussian spectral shape.

    `GAUSS [sigfr]`

    """

    model_type: Literal["gauss"] = Field(
        default="gauss", description="Model type discriminator"
    )
    sigfr: confloat(gt=0.0) = Field(
        description=(
            "Width of the Gaussian frequency spectrum expressed "
            "as a standard deviation in Hz."
        ),
    )

    def cmd(self) -> str:
        return f"{super().cmd()} sigfr={self.sigfr}"


class PM(BaseSubComponent):
    """Pearson-Moskowitz spectral shape.

    `PM`

    """

    model_type: Literal["pm"] = Field(
        default="pm", description="Model type discriminator"
    )


class BIN(BaseSubComponent):
    """Single frequency bin spectral shape.

    `BIN`

    """

    model_type: Literal["bin"] = Field(
        default="bin", description="Model type discriminator"
    )


class SHAPESPEC(BaseSubComponent):
    """SWAN BOUND SHAPESPEC subcomponent.

    `BOUND SHAPESPEC JONSWAP|PM|GAUSS|BIN|TMA PEAK|MEAN DSPR [POWER|DEGREES]`

    This command BOUND SHAPESPEC defines the shape of the spectra (both in frequency
    and direction) at the boundary of the computational grid in case of parametric
    spectral input.

    """

    model_type: Literal["shapespec"] = Field(
        default="shapespec", description="Model type discriminator"
    )
    shape: JONSWAP | PM | GAUSS | BIN | TMA = Field(
        default=JONSWAP(),
        description="The spectral shape",
    )
    per_type: Literal["peak", "mean"] = Field(
        default="peak",
        description="The type of characteristic wave period",
    )
    dspr_type: Literal["power", "degrees"] = Field(
        default="power",
        description="The type of directional spreading",
    )

    def cmd(self) -> str:
        repr = (
            f"BOUND SHAPESPEC {self.shape.render()} {self.per_type.upper()} "
            f"DSPR {self.dspr_type.upper()}"
        )
        return repr
