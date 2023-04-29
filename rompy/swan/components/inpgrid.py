"""Input grid for SWAN."""

from rompy.swan.components.base import BaseComponent, FormatEnum


class InpGrid(BaseComponent):
    """SWAN input grid."""
    name: str = "Input data"

    def __repr__(self):
        return "INPGRID"