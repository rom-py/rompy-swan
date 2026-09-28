"""Test that the lockup commands follow the SWAN mode."""

import pytest
from pydantic import ValidationError

from rompy.core.time import TimeRange
from rompy.model import ModelRun
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.group import LOCKUP, STARTUP
from rompy_swan.components.lockup import COMPUTE_NONSTAT, COMPUTE_STAT
from rompy_swan.components.startup import MODE
from rompy_swan.config import SwanConfig
from rompy_swan.subcomponents.time import NONSTATIONARY

CGRID = REGULAR(
    grid=dict(xp=0, yp=0, alp=0, xlen=1000, ylen=1000, mx=10, my=10),
    spectrum=dict(mdc=36, flow=0.04, fhigh=1.0),
)
PERIOD = TimeRange(start="2023-01-01T00", end="2023-01-01T06", interval="1h")


def input_file(config, tmp_path) -> str:
    run = ModelRun(run_id="run", period=PERIOD, output_dir=tmp_path, config=config)
    return (tmp_path / "run" / "INPUT").read_text() if run.generate() else ""


@pytest.mark.parametrize("startup", [None, STARTUP(mode=MODE(kind="stationary"))])
def test_stationary_mode_writes_compute_without_times(tmp_path, startup):
    config = SwanConfig(
        cgrid=CGRID, startup=startup, lockup=LOCKUP(compute=COMPUTE_STAT())
    )
    lines = input_file(config, tmp_path).splitlines()
    assert "COMPUTE" in lines
    assert not any(line.startswith("COMPUTE ") for line in lines)


def test_nonstationary_mode_writes_compute_times(tmp_path):
    config = SwanConfig(
        cgrid=CGRID,
        startup=STARTUP(mode=MODE(kind="nonstationary")),
        lockup=LOCKUP(compute=COMPUTE_STAT()),
    )
    assert "COMPUTE STATIONARY time=20230101.000000" in input_file(config, tmp_path)


@pytest.mark.parametrize(
    "compute",
    [COMPUTE_NONSTAT(), COMPUTE_STAT(times=NONSTATIONARY())],
    ids=["nonstationary", "stationary-series"],
)
def test_stationary_mode_rejects_timed_computations(compute):
    with pytest.raises(ValidationError, match="stationary mode"):
        SwanConfig(cgrid=CGRID, lockup=LOCKUP(compute=compute))


def test_stationary_mode_rejects_time_stamped_inputs():
    from rompy.core.source import SourceFile
    from rompy_swan.data import SwanDataGrid
    from rompy_swan.interface import DataInterface

    source = SourceFile(uri="wind.nc")
    inpgrid = DataInterface(
        bottom=SwanDataGrid(var="bottom", z1="depth", source=source),
        input=[SwanDataGrid(var="wind", z1="u10", z2="v10", source=source)],
    )
    with pytest.raises(ValidationError, match="used by the wind input"):
        SwanConfig(cgrid=CGRID, inpgrid=inpgrid)
    SwanConfig(
        cgrid=CGRID, inpgrid=inpgrid, startup=STARTUP(mode=MODE(kind="nonstationary"))
    )


def test_stationary_mode_writes_output_without_times(tmp_path):
    from rompy_swan.components.group import OUTPUT
    from rompy_swan.components.output import BLOCK

    output = OUTPUT(block=BLOCK(sname="COMPGRID", fname="grid.nc", output=["hsign"]))
    config = SwanConfig(
        cgrid=CGRID, output=output, lockup=LOCKUP(compute=COMPUTE_STAT())
    )
    assert "tbegblk" not in input_file(config, tmp_path)


def test_stationary_mode_rejects_output_times():
    from rompy_swan.components.group import OUTPUT
    from rompy_swan.components.output import BLOCK

    block = BLOCK(
        sname="COMPGRID", fname="grid.nc", output=["hsign"], times=dict(delt="PT1H")
    )
    with pytest.raises(ValidationError, match="output components with times"):
        SwanConfig(cgrid=CGRID, output=OUTPUT(block=block))
