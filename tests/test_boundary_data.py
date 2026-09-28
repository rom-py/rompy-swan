"""Test the data-driven boundary classes."""

from pathlib import Path

import pandas as pd
import pytest

from rompy.core.source import SourceFile
from rompy.core.time import TimeRange
from rompy_swan.boundary import BoundspecSegmentXY, BoundspecSide, write_tpar
from rompy_swan.grid import SwanGrid
from rompy_swan.interface import BoundaryInterface
from rompy_swan.subcomponents.boundary import SIDE

HERE = Path(__file__).parent


@pytest.fixture(scope="module")
def grid():
    return SwanGrid(x0=110, y0=-35.2, rot=0, dx=0.5, dy=0.5, nx=15, ny=10)


@pytest.fixture(scope="module")
def time():
    return TimeRange(start="2023-01-01T00", end="2023-01-01T12", interval="6h")


@pytest.fixture(scope="module")
def source():
    return SourceFile(uri=HERE / "data" / "aus-20230101.nc")


@pytest.mark.parametrize("cls", [BoundspecSide, BoundspecSegmentXY])
def test_boundspec_writes_shapespec(tmp_path, grid, time, source, cls):
    bnd = cls(
        id="wave",
        source=source,
        location=SIDE(side="west", direction="ccw"),
        sel_method="idw",
        sel_method_kwargs={"tolerance": 4.0},
    )
    _, cmd = bnd.get(destdir=tmp_path, grid=grid, time=time)
    first, *rest = cmd.splitlines()
    assert first.startswith("BOUND SHAPESPEC")
    assert "DSPR DEGREES" in first
    assert rest and all(line.startswith("BOUNDSPEC") for line in rest)


def test_write_tpar_rejects_missing_values(tmp_path):
    times = pd.date_range("2023-01-01", periods=2, freq="h")
    df = pd.DataFrame({"hs": [1.0, None], "tp": [10.0, 10.0]}, index=times)
    with pytest.raises(ValueError, match="Missing values"):
        write_tpar(df, tmp_path / "bnd.txt")


def test_boundary_model_types_are_unique(source):
    kwargs = dict(id="wave", source=source, location=SIDE(side="west"))
    assert BoundspecSide(**kwargs).model_type != BoundspecSegmentXY(**kwargs).model_type


@pytest.mark.parametrize("cls", [BoundspecSide, BoundspecSegmentXY])
def test_boundary_interface_parses_kind_from_dict(source, cls):
    kind = cls(id="wave", source=source, location=SIDE(side="west"))
    interface = BoundaryInterface(kind=kind.model_dump())
    assert type(interface.kind) is cls


def test_boundnest1_rejects_missing_spectra(tmp_path, grid, time, source):
    from rompy_swan.boundary import Boundnest1

    bnd = Boundnest1(
        id="wave", source=source, sel_method="idw", sel_method_kwargs={"tolerance": 0.1}
    )
    with pytest.raises(ValueError, match="Missing spectra"):
        bnd.get(destdir=tmp_path, grid=grid, time=time)


def test_boundnest1_writes_complete_spectra(tmp_path, grid, time, source):
    from rompy_swan.boundary import Boundnest1

    bnd = Boundnest1(
        id="wave",
        source=source,
        sel_method="nearest",
        sel_method_kwargs={"tolerance": 4.0},
    )
    filename, cmd = bnd.get(destdir=tmp_path, grid=grid, time=time)
    assert cmd.startswith("BOUNDNEST1 NEST")
    assert "nan" not in filename.read_text().lower()


def test_segments_have_no_repeated_points(source):
    from rompy_swan.subcomponents.boundary import SIDES

    grid = SwanGrid(x0=114.5, y0=-32.8, dx=0.02, dy=0.02, nx=71, ny=66)
    sides = SIDES(
        sides=[
            SIDE(side="south", direction="clockwise"),
            SIDE(side="west", direction="clockwise"),
        ]
    )
    bnd = BoundspecSegmentXY(id="wave", source=source, location=sides, spacing=0.325)
    x, y = bnd._boundary_points(grid)
    steps = [abs(x1 - x0) + abs(y1 - y0) for x0, x1, y0, y1 in zip(x, x[1:], y, y[1:])]
    assert min(steps) > 1e-6
