"""SWAN boundary classes."""
import logging
from pathlib import Path
from typing import Literal, Optional, Union

import numpy as np
from pydantic import Field, model_validator

from rompy.core.time import TimeRange
from rompy.core.boundary import BoundaryWaveStation
from rompy.swan.grid import SwanGrid


logger = logging.getLogger(__name__)


class Boundnest1(BoundaryWaveStation):
    """SWAN BOUNDNEST1 NEST data class."""

    model_type: Literal["boundnest1", "BOUNDNEST1"] = "boundnest1"
    rectangle: Literal["closed", "open"] = Field(
        default="closed",
        description=(
            "Defines whether boundary is defined over an closed or open rectangle"
        ),
    )

    def get(
        self, destdir: str, grid: SwanGrid, time: Optional[TimeRange] = None
    ) -> str:
        """Write the data source to a new location.

        Parameters
        ----------
        destdir : str | Path
            Destination directory for the SWAN ASCII file.
        grid : RegularGrid
            Grid instance to use for selecting the boundary points.
        time: TimeRange, optional
            The times to filter the data to, only used if `self.crop_data` is True.

        Returns
        -------
        cmd : str
            Boundary command string to render in the SWAN INPUT file

        """
        if self.crop_data and time is not None:
            self._filter_time(time)
        ds = self._sel_boundary(grid)
        filename = Path(destdir) / f"{self.id}.bnd"
        ds.spec.to_swan(filename)
        cmd = f"BOUNDNEST1 NEST '{filename.name}' {self.rectangle.upper()}"
        return cmd
