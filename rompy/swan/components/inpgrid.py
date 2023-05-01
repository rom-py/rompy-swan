"""Input grid for SWAN."""
from typing_extensions import Literal

from rompy.swan.components.base import BaseComponent, FormatEnum


class InpGrid(BaseComponent):
    """SWAN input grid.

    Parameters
    ----------
    kind : Literal["InpGrid"]
        Name of the component to help parsing and render as a comment in the cmd file.

    """
    kind: Literal["InpGrid"] = "InpGrid"

    def __repr__(self):
        return "INPGRID"
