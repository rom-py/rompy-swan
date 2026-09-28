"""Test the SWAN input grid writers."""

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import rompy_swan.data  # noqa: F401  (registers the .swan accessor)


@pytest.fixture
def dset():
    times = pd.date_range("2023-01-01", periods=3, freq="h")
    lat = np.array([-33.0, -32.5, -32.0])
    lon = np.array([114.0, 114.5])
    u = np.ones((3, lat.size, lon.size))
    u[:, 0, 0] = np.nan
    return xr.Dataset(
        {"u10": (("time", "lat", "lon"), u), "v10": (("time", "lat", "lon"), u)},
        coords={"time": times, "lat": lat, "lon": lon},
    )


def test_inpgrid_fills_missing_values(tmp_path, dset):
    outfile = tmp_path / "wind.grd"
    inpgrid, _ = dset.swan.to_inpgrid(outfile, var="WIND", z1="u10", z2="v10")
    assert "nan" not in outfile.read_text().lower()
    assert "EXC -99.0" in inpgrid


def test_inpgrid_writes_rows_along_latitude(tmp_path, dset):
    """Rows are written along y even when the dataset has (time, lon, lat) order."""
    outfile = tmp_path / "wind.grd"
    dset.transpose("time", "lon", "lat").swan.to_inpgrid(outfile, z1="u10", z2="v10")
    first_block = outfile.read_text().splitlines()[1:4]
    assert [len(row.split()) for row in first_block] == [2, 2, 2]


def test_inpgrid_needs_two_times(tmp_path, dset):
    with pytest.raises(ValueError, match="at least two times"):
        dset.isel(time=[0]).swan.to_inpgrid(tmp_path / "wind.grd", z1="u10")


def test_exception_value_scaled_by_fac(tmp_path, dset):
    """SWAN compares the exception value after multiplying by fac."""
    bottom = dset.isel(time=0).rename(u10="elevation")
    inpgrid, readinp = bottom.swan.to_bottom_grid(
        tmp_path / "bottom.grd", z="elevation", fac=-1.0
    )
    assert "EXC 99.0" in inpgrid
    assert "READINP BOTTOM -1.0" in readinp
