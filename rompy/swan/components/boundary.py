"""Boundary for SWAN."""
from typing import Literal, Optional, Any
from pathlib import Path
from typing_extensions import Literal
from pydantic import root_validator, confloat

from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.shape import SHAPESPEC
from rompy.swan.subcomponents.boundary import (
    SIDE,
    SEGMENTXY,
    SEGMENTIJ,
    CONSTANTPAR,
    VARIABLEPAR,
    CONSTANTFILE,
    VARIABLEFILE,
)


HERE = Path(__file__).parent


class BOUNDSPEC(BaseComponent):
    """SWAN BOUNDSPEC boundary component.

    `BOUNDSPEC SIDE|SEGMENT ... CONSTANT|VARIABLE PAR|FILE ...`

    This command BOUNDSPEC defines parametric spectra at the boundary. It consists of
    two parts, the first part defines the boundary side or segment where the spectra
    will be given, the second part defines the spectral parameters of these spectra.
    Note that in fact only the incoming wave components of these spectra are used by
    SWAN. The fact that complete spectra are calculated at the model boundaries from
    the spectral parameters should not be misinterpreted. Only the incoming components
    are effective in the computation.

    Parameters
    ----------
    model_type: Literal["boundspec"]
        Model type discriminator.
    shapespec: Optional[SHAPESPEC]
        Spectral shape specification.
    location: SIDE | SEGMENTXY | SEGMENTIJ
        Location to apply th boundary.
    data: CONSTANTPAR | CONSTANTFILE | VARIABLEPAR | VARIABLEFILE
        Spectral data.

    TODO: Add support for unstructured grid (k).

    """

    model_type: Literal["boundspec"] = "boundspec"
    shapespec: SHAPESPEC = SHAPESPEC()
    location: SIDE | SEGMENTXY | SEGMENTIJ
    data: CONSTANTPAR | CONSTANTFILE | VARIABLEPAR | VARIABLEFILE

    def __repr__(self):
        repr = f"{self.shapespec.render()}\n"
        repr += f"BOUNDSPEC {self.location.render()}{self.data.render()}"
        return repr
