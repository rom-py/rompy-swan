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

    """
    model_type: Literal["forcing", "FORCING"] = Field(
        default="forcing", description="Model type discriminator"
    )
    bottom: Optional[SwanDataGrid] = Field(default=None, description="Bathymetry data")
    wind: Optional[SwanDataGrid] = Field(default=None, description="Wind input data")
    current: Optional[SwanDataGrid] = Field(
        default=None, description="Current input data"
    )
    boundary: Optional[DataBoundary] = Field(
        default=None, description="Boundary input data"
    )

    def get(self, grid: SwanGrid, period: TimeRange, staging_dir: Path):
        forcing = []
        boundary = []
        for source in self:
            if source[1]:
                logger.info(f"\t Processing {source[0]} forcing")
                source[1]._filter_grid(grid)
                source[1]._filter_time(period)
                if source[0] == "boundary":
                    boundary.append(source[1].get(staging_dir, grid))
                else:
                    forcing.append(source[1].get(staging_dir, grid))
        return dict(forcing="\n".join(forcing), boundary="\n".join(boundary))

    def __str__(self):
        ret = ""
        for forcing in self:
            if forcing[1]:
                ret += f"\t{forcing[0]}: {forcing[1].source}\n"
        return ret