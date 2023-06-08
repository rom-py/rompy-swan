"""SWAN boundary classes."""
from abc import ABC, abstractmethod
from typing import Literal, Optional
from pathlib import Path
from pydantic import Field, root_validator, confloat
import intake
import xarray as xr
import wavespectra
import numpy as np

from rompy.core.time import TimeRange
from rompy.core.types import RompyBaseModel
from rompy.core.filters import Filter
from rompy.core.data import DataBlob
from rompy.swan.grid import SwanGrid


def find_minimum_distance(points: list[tuple[float, float]]) -> float:
    """Find the minimum distance between a set of points.

    Parameters
    ----------
    points: list[tuple[float, float]]
        List of points as (x, y) tuples.

    Returns
    -------
    min_distance: float
        Minimum distance between all points.

    """

    def calculate_distance(x1, y1, x2, y2):
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    n = len(points)
    if n <= 1:
        return float("inf")

    # Sort points by x-coordinate
    points.sort()

    # Recursive step
    if n == 2:
        return calculate_distance(*points[0], *points[1])

    mid = n // 2
    left_points = points[:mid]
    right_points = points[mid:]

    # Divide and conquer
    left_min = find_minimum_distance(left_points)
    right_min = find_minimum_distance(right_points)

    min_distance = min(left_min, right_min)

    # Find the closest pair across the dividing line
    strip = []
    for point in points:
        if abs(point[0] - points[mid][0]) < min_distance:
            strip.append(point)

    strip_min = min_distance
    strip_len = len(strip)
    for i in range(strip_len - 1):
        j = i + 1
        while j < strip_len and (strip[j][1] - strip[i][1]) < strip_min:
            distance = calculate_distance(*strip[i], *strip[j])
            if distance < strip_min:
                strip_min = distance
            j += 1

    return min(min_distance, strip_min)


class Dataset(RompyBaseModel, ABC):
    """Abstract base class for a dataset."""

    @abstractmethod
    def open(self):
        """Return a dataset instance with the wavespectra accessor."""
        pass


class DatasetXarray(Dataset):
    """Wavespectra dataset from xarray reader."""

    model_type: Literal["xarray"] = Field(
        default="xarray",
        description="Model type discriminator",
    )
    uri: str | Path = Field(description="Path to the dataset")
    engine: Optional[str] = Field(
        default=None,
        description="Engine to use for reading the dataset with xarray.open_dataset",
    )
    kwargs: dict = Field(
        default={},
        description="Keyword arguments to pass to xarray.open_dataset",
    )

    def open(self):
        return xr.open_dataset(self.uri, engine=self.engine, **self.kwargs)


class DatasetIntake(Dataset):
    """Wavespectra dataset from intake catalog."""

    model_type: Literal["intake"] = Field(
        default="intake",
        description="Model type discriminator",
    )
    dataset_id: str = Field(description="The id of the dataset to read in the catalog")
    catalog_uri: str | Path = Field(description="The URI of the catalog to read from")
    kwargs: dict = Field(
        default={},
        description="Keyword arguments to pass to intake.open_catalog",
    )

    def open(self):
        cat = intake.open_catalog(self.catalog_uri)
        return cat[self.dataset_id](**self.kwargs).to_dask()


class DatasetWavespectra(Dataset):
    """Wavespectra dataset from wavespectra reader."""

    model_type: Literal["wavespectra"] = Field(
        default="wavespectra",
        description="Model type discriminator",
    )
    uri: str | Path = Field(description="Path to the dataset")
    reader: str = Field(
        description="Name of the wavespectra reader to use, e.g., read_swan",
    )
    kwargs: dict = Field(
        default={},
        description="Keyword arguments to pass to wavespectra.read_swan",
    )

    def open(self):
        return getattr(wavespectra, self.reader)(self.uri, **self.kwargs)


class DataBoundary(RompyBaseModel):
    """SWAN BOUNDNEST1 NEST data class."""

    id: str = Field(description="Unique identifier for this data source")
    dataset: DatasetXarray | DatasetIntake | DatasetWavespectra = Field(
        description="Dataset reader, must return a wavespectra-enabled xarray dataset in the open method",
        discriminator="model_type"
    )
    grid: Optional[SwanGrid] = Field(
        default=None,
        description="Grid specification to use for selecting boundary points from the dataset",
    )
    sel_method: Literal["idw", "nearest"] = Field(
        default="idw",
        description="Wavespectra method to use for selecting boundary points from the dataset",
    )
    tolerance: confloat(ge=0) = Field(
        default=1.0,
        description="Wavespectra tolerance for selecting boundary points from the dataset",
    )
    rectangle: Literal["closed", "open"] = Field(
        default="closed",
        description="Defines whether boundary is defined over an closed or open rectangle",
    )
    filter: Optional[Filter] = Field(
        default=Filter(),
        description="Optional filter specification to apply to the dataset",
    )

    @root_validator
    def assert_has_wavespectra_accessor(cls, values):
        dataset = values.get("dataset")
        if dataset is not None:
            dset = dataset.open()
            if not hasattr(dset, "spec"):
                raise ValueError(f"Wavespectra compatible dataset is required")
        return values

    @property
    def ds(self):
        """Return the filtered xarray dataset instance."""
        return self.filter(self.dataset.open())

    def _boundary_resolutions(self, grid):
        """Boundary resolution based on the shortest distance between points.

        The boundary resolution should be based on the dataset resolution instead of
        the grid resolution to avoid creating points unecessarily. Here we find the
        minimum distance between points in the dataset and use that to define the
        boundary resolution ensuring the grid sizes are divisible by the resolution.

        """
        # Find out the minimum distance between points in the original dataset
        buffer = 2 * min(grid.dx, grid.dy)
        x0, y0, x1, y1 = grid.bbox(buffer=buffer)
        # Select dataset points just outside the actual grid to optimise the search
        ds = self.ds.spec.sel([x0, x1], [y0, y1], method="bbox")
        points = list(zip(ds.lon.values, ds.lat.values))
        min_distance = find_minimum_distance(points)
        # Calculate resolutions ensuring at least 3 points per side
        xlen = grid.maxx - grid.minx
        nx = max(xlen // min_distance, 3)
        dx = xlen / nx
        ylen = grid.maxy - grid.miny
        ny = max(ylen // min_distance, 3)
        dy = ylen / ny
        return dx, dy

    def _boundary_points(self, grid):
        """Coordinates of boundary points based on grid bbox and dataset resolution."""
        x0, y0, x1, y1 = grid.bbox(buffer=0)
        dx, dy = self._boundary_resolutions(grid)
        x = np.clip(np.arange(x0, x1 + dx, dx), x0, x1)
        y = np.clip(np.arange(y0, y1 + dy, dy), y0, y1)
        xbnd = np.concatenate(
            (
                x,
                np.repeat(x[-1], y.size - 1),
                x[-2::-1],
                np.repeat(x[0], y.size - 1),
            )
        )
        ybnd = np.concatenate(
            (
                np.repeat(y[0], x.size),
                y[1:],
                np.repeat(y[-1], x.size - 1),
                y[-2::-1],
            )
        )
        return xbnd, ybnd

    def _filter_grid(self, grid, buffer=0.1):
        """Required by SwanForcing"""
        self.grid = grid

    def _filter_time(self, time: TimeRange):
        """Time filter"""
        self.filter.crop.update({"time": slice(time.start, time.end)})

    def get(self, stage_dir: str) -> str:
        """Write the data source to a new location"""
        if self.grid is None:
            raise ValueError("grid must be defined before calling get")
        xbnd, ybnd = self._boundary_points(self.grid)
        ds = self.ds.spec.sel(
            lons=xbnd,
            lats=ybnd,
            method=self.sel_method,
            tolerance=self.tolerance,
        )
        filename = Path(stage_dir) / f"{self.id}.bnd"
        ds.spec.to_swan(filename)
        cmd = f"BOUNDNEST1 NEST '{filename}' {self.rectangle.upper()}"
        return cmd
