"""Boundary for SWAN."""
import yaml
from enum import Enum
from typing import Literal, Optional
from enum import Enum
from pathlib import Path
from typing_extensions import Literal
from pydantic import root_validator, confloat

from rompy.swan.components.base import BaseComponent#, NONSTATIONARY, READINP, GridOptions
from rompy.swan.types import BoundShapeOptions, SideOptions
from rompy.swan.components.subcomponents import SIDE, SEGMENTXY, SEGMENTIJ, CONSTANTPAR, VARIABLEPAR, CONSTANTFILE


HERE = Path(__file__).parent


class BOUNDARY(BaseComponent):
    """SWAN boundary.

    This is the base class for boundary. It is not meant to be used directly.

    Parameters
    ----------
    model_type: Literal["boundary"]
        Model type discriminator.

    """

    model_type: Literal["boundary"] = "boundary"

    # @root_validator
    # def set_nonstat_suffix(cls, values):
    #     """Set the nonstationary suffix."""
    #     if values.get("nonstationary") is not None:
    #         values["nonstationary"].suffix = "inp"
    #     if values.get("grid_type") is not None and "grid_type" in values:
    #         values["readinp"].grid_type = values["grid_type"]
    #     return values

    def __repr__(self):
        raise RuntimeError("BOUNDARY is an abstract class and cannot be rendered.")


class SHAPESPEC(BOUNDARY):
    """SWAN SHAPespec base class.

    This command BOUND SHAPESPEC defines the shape of the spectra (both in frequency
    and direction) at the boundary of the computational grid in case of parametric
    spectral input.

    Parameters
    ----------
    model_type: Literal["shapespec"]
        Model type discriminator.
        Peak enhancement parameter of the JONSWAP spectrum.
    per_type: Literal['peak', 'mean']
        The type of characteristic wave period 
    dspr_type: Literal['power', 'degrees']

    """

    model_type: Literal["shapespec"] = "shapespec"
    per_type: Literal["peak", "mean"] = "peak"
    dspr_type: Literal["power", "degrees"] = "power"

    # def render(self):
    #     raise RuntimeError("SHAPESPEC is an abstract class and cannot be rendered.")


class JONSWAP(SHAPESPEC):
    """SWAN SHAPespec JONSWAP boundary."""

    model_type: Literal["jonswap"] = "jonswap"
    gamma: confloat(gt=0.0) = 3.3

    def render(self):
        repr = (
            f"BOUND SHAPESPEC JONSWAP gamma={self.gamma} {self.per_type.upper()} "
            f"DSPR {self.dspr_type.upper()}"
        )
        return repr


class BOUNDSPEC(BOUNDARY):
    """SWAN BOUNDSPEC boundary component.

    `BOUNDSPEC`

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
    location: SIDE | SEGMENTXY | SEGMENTIJ
        Location to apply th boundary.
    k: int
        Index of boundary vertex of the segment. This can be obtained in a grid
        generator file (fort.14, .node and .n files of ADCIRC, Triangle and
        Easymesh, respectively). The order must be counterclockwise!
        ONLY MEANT FOR UNSTRUCTURED MESHES.

    TODO: Add BOUnd SHAPespec

    """
    model_type: Literal["boundspec"] = "boundspec"
    location: SIDE | SEGMENTXY | SEGMENTIJ
    data: CONSTANTPAR | CONSTANTFILE | VARIABLEPAR

    def __repr__(self):
        repr = f"BOUNDSPEC {self.location.render()}{self.data.render()}"
        return repr


from pydantic import BaseModel



if __name__ == "__main__":
    bnd = SIDE(side="west")
    print(bnd.render())
