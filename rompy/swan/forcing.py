"""SWAN Forcing data."""
import logging
from typing import Union, Annotated, Optional, Literal
from pathlib import Path
from pydantic import Field

from rompy.core import RompyBaseModel, TimeRange
from rompy.swan.grid import SwanGrid
from rompy.swan.data import SwanDataGrid
from rompy.swan.boundary import DataBoundary


logger = logging.getLogger(__name__)


class ForcingData(RompyBaseModel):
    """SWAN forcing data.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy.swan.forcing import ForcingData

    TODO: Should we simplify it and have one single list field?

    """
    model_type: Literal["forcing", "FORCING"] = Field(
        default="forcing", description="Model type discriminator"
    )
    bottom: Optional[SwanDataGrid] = Field(default=None, description="Bathymetry data")
    input: list[SwanDataGrid] = Field(default=[], description="Input grid data")
    boundary: Optional[DataBoundary] = Field(default=None, description="Boundary data")

    def get(self, grid: SwanGrid, period: TimeRange, staging_dir: Path):
        cmds = []
        # Bottom grid
        if self.bottom is not None:
            self.bottom._filter_grid(grid)
            self.bottom._filter_time(period)
            cmds.append(self.bottom.get(staging_dir, grid))
        # Input grids
        for input in self.input:
            input._filter_grid(grid)
            input._filter_time(period)
            cmds.append(input.get(staging_dir, grid))
        # Boundary data
        if self.boundary is not None:
            self.boundary._filter_grid(grid)
            self.boundary._filter_time(period)
            cmds.append(self.boundary.get(staging_dir, grid))
        return "\n".join(cmds)

    def render(self, *args, **kwargs):
        """Make this class consistent with the components API."""
        return self.get(*args, **kwargs)

    def __str__(self):
        ret = ""
        if self.bottom:
            ret += self.bottom.source
        for input in self.input:
            ret += input.source
        if self.boundary:
            ret += self.boundary.source
        return ret
