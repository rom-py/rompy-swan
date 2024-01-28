"""SWAN boundary classes."""
import logging
from pathlib import Path
from typing import Literal, Optional, Union, Annotated
import xarray as xr
import pandas as pd
import numpy as np
from abc import ABC
from pydantic import Field, field_validator

from rompy.core.time import TimeRange
from rompy.core.boundary import BoundaryWaveStation
from rompy.swan.grid import SwanGrid
from rompy.swan.components.boundary import BOUNDSPEC
from rompy.swan.subcomponents.base import BaseSubComponent, XY, IJ
from rompy.swan.subcomponents.boundary  import SIDE, SIDES, SEGMENT, VARIABLEFILE, VARIABLEPAR, CONSTANTFILE, CONSTANTPAR
from rompy.swan.subcomponents.spectrum import SHAPESPEC

logger = logging.getLogger(__name__)


def write_tpar(df: pd.DataFrame, filename: str | Path):
    """Write TPAR file.

    Parameters
    ----------
    df : pandas.DataFrame
        TPAR dataframe.
    filename : str | Path
        Filename to write to.

    """
    with open(filename, "w") as stream:
        stream.write("TPAR\n")
        df.to_csv(
            stream,
            sep=" ",
            na_rep=0.0,
            header=False,
            float_format="%0.2f",
            date_format="%Y%m%d.%H%M%S",
        )


class Boundnest1(BoundaryWaveStation):
    """SWAN BOUNDNEST1 NEST data class."""

    model_type: Literal["boundnest1", "BOUNDNEST1"] = Field(
        default="boundnest1", description="Model type discriminator"
    )
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
        ds = self._sel_boundary(grid).sortby("dir")
        filename = Path(destdir) / f"{self.id}.bnd"
        ds.spec.to_swan(filename)
        cmd = f"BOUNDNEST1 NEST '{filename.name}' {self.rectangle.upper()}"
        return cmd


class BoundspecBase(BoundaryWaveStation, ABC):
    """Base class for SWAN BOUNDSPEC data classes."""
    model_type: Literal["boundspecbase", "BOUNDSPECBASE"] = Field(
        default="boundspecbase", description="Model type discriminator"
    )
    shapespec: SHAPESPEC = Field(
        description="Spectral shape specification",
        default=SHAPESPEC(dspr_type="degrees"),
    )
    variable: bool = Field(
        description="Whether the spectra can vary along the side", default=False
    )
    file_type: Literal["tpar", "spec2d"] = Field(
        default="tpar", description="The type of file to write"
    )
    _ds: None

    @field_validator("variable")
    @classmethod
    def variable_not_implemented(cls, v, values):
        if v is True:
            raise NotImplementedError("Variable spectra not implemented yet")
        return v

    @property
    def per(self) -> str:
        if self.shapespec.per_type == "peak":
            return "tp"
        elif self.shapespec.per_type == "mean":
            return "tm01"

    @property
    def dspr(self) -> str:
        if self.shapespec.dspr_type == "degrees":
            return "dspr"
        elif self.shapespec.dspr_type == "power":
            raise NotImplementedError("Power of cos not supported yet")

    @property
    def tpar(self) -> pd.DataFrame:
        """TPAR dataframe for the _ds attr."""
        return self._ds.spec.stats(["hs", self.per, "dpm", self.dspr]).to_pandas()

    def _boundary_points_side(self, grid, side):
        """Coordinates of boundary points on a grid side."""
        # Return the boundary points in CCW orderf
        if side.side == "south":
            slc = np.s_[0, :]
        elif side.side == "east":
            slc = np.s_[:, -1]
        elif side.side == "north":
            slc = np.s_[-1, ::-1]
        elif side.side == "west":
            slc = np.s_[::-1, 0]
        elif side.side == "sw":
            slc = np.s_[0, 0]
        elif side.side == "se":
            slc = np.s_[0, -1]
        elif side.side == "nw":
            slc = np.s_[-1, 0]
        elif side.side == "ne":
            slc = np.s_[-1, -1]
        xbnd = grid.x[slc]
        ybnd = grid.y[slc]
        # Reverse if order is clockwise
        if side.direction == "clockwise":
            xbnd = np.flip(xbnd)
            ybnd = np.flip(ybnd)
        return xbnd, ybnd


class BoundspecSide(BoundspecBase):
    """SWAN BOUNDSPEC SIDE data class.

    TODO: Handle side definition on a rotated grid.
    TODO: Should SIDE VARIABE be supported?
    TODO: Support option to choose between mid-point or averaging?
    TODO: Does PAR need to be supported? Guess not as nonstationary isn't supported

    Note
    ----
    The 'spec1d' file type is not supported yet.

    """

    model_type: Literal["boundspecside", "BOUNDSPECSIDE"] = Field(
        default="boundspecside", description="Model type discriminator"
    )
    location: SIDE = Field(description="The side of the grid to apply the boundary to")

    def _boundary_points(self, grid) -> tuple:
        """Coordinates of boundary points at midpoint of a grid side."""
        xbnd, ybnd = self._boundary_points_side(grid, self.location.side)
        return [xbnd.mean()], [ybnd.mean()]

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
        ds = self._sel_boundary(grid).sortby("dir")

        cmds = []
        for ind in range(ds.lon.size):
            self._ds = ds.isel(site=ind, drop=True)
            filename = f"{self.id}_{self.file_type}_{self.location.side}_{ind:03d}.bnd"
            if self.file_type == "tpar":
                write_tpar(self.tpar, Path(destdir) / filename)
            elif self.file_type == "spec2d":
                self._ds.spec.to_swan(Path(destdir) / filename)
            comp = CONSTANTFILE(fname=filename, seq=1)
            cmds.append(f"BOUNDSPEC {self.location.render()}{comp.render()}")
        return "\n".join(cmds)


class BoundspecSegmentXY(BoundspecBase):
    """SWAN BOUNDSPEC SEGMENT data class.

    TODO: Handle side definition on a rotated grid.
    TODO: Should SIDE VARIABE be supported?
    TODO: Support option to choose between mid-point or averaging?
    TODO: Does PAR need to be supported? Guess not as nonstationary isn't supported
    TODO: If SIDES, ensure continuous
    TODO: Option to close each side
    TODO: Avoid duplicate points from SIDES

    Note
    ----
    Segments are defined from adjacent point locations so the order in which the points
    are defined is important. When using SIDES, please ensure SIDES are adjacent to
    each other and have correct directions (ccw or clockwise) accordint to the order in
    which each side is prescribed.

    Note
    ----
    The 'spec1d' file type is not supported yet.

    """

    model_type: Literal["boundspecside", "BOUNDSPECSIDE"] = Field(
        default="boundspecside", description="Model type discriminator"
    )
    location: Union[SIDE, SIDES, XY] = Field(
        description="The side of the grid to apply the boundary to",
        discriminator="model_type",
    )

    def _boundary_points(self, grid) -> tuple:
        """Coordinates of boundary points along the segment."""
        if isinstance(self.location, XY):
            xbnd, ybnd = self.location.x, self.location.y
        elif isinstance(self.location, SIDE):
            xbnd, ybnd = self._boundary_points_side(grid, self.location)
        elif isinstance(self.location, SIDES):
            xbnd, ybnd = [], []
            for location in self.location.sides:
                xb, yb = self._boundary_points_side(grid, location)
                xbnd.extend(xb)
                ybnd.extend(yb)
        return xbnd, ybnd

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
        ds = self._sel_boundary(grid).sortby("dir")

        # If nearest, ensure points are returned at the requested positions
        if self.sel_method == "nearest":
            xbnd, ybnd = self._boundary_points(grid=grid)
            ds["lon"].values = xbnd
            ds["lat"].values = ybnd

        cmds = []
        for ind in range(ds.lon.size - 1):
            ds_seg = ds.isel(site=slice(ind, ind+2))
            # TODO: Ensure points in segment are different
            self._ds = ds_seg.mean("site")
            filename = f"{self.id}_{self.file_type}_{ind:03d}.bnd"
            if self.file_type == "tpar":
                write_tpar(self.tpar, Path(destdir) / filename)
            elif self.file_type == "spec2d":
                self._ds.spec.to_swan(Path(destdir) / filename)
            file = CONSTANTFILE(fname=filename, seq=1)
            location = SEGMENT(points=XY(x=ds_seg.lon.values, y=ds_seg.lat.values))
            location = location.render().replace("\n", " ").replace("  ", " ")
            cmds.append(f"BOUNDSPEC {location}{file.render()}")
        return "\n".join(cmds)
