"""Test that the computation, inputs and output follow the SWAN mode."""

import pytest
from pydantic import ValidationError

from rompy.core.time import TimeRange
from rompy.model import ModelRun
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.group import LOCKUP, STARTUP
from rompy_swan.components.lockup import COMPUTE, COMPUTE_NONSTAT, COMPUTE_STAT
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
        cgrid=CGRID,
        startup=startup,
        lockup=LOCKUP(compute=COMPUTE(hotfile=dict(fname="hotfile"))),
    )
    lines = input_file(config, tmp_path).splitlines()
    assert lines[-3:] == ["COMPUTE", "HOTFILE fname='hotfile'", "STOP"]


def test_nonstationary_mode_writes_compute_times(tmp_path):
    config = SwanConfig(
        cgrid=CGRID,
        startup=STARTUP(mode=MODE(kind="nonstationary")),
        lockup=LOCKUP(compute=COMPUTE_STAT()),
    )
    assert "COMPUTE STATIONARY time=20230101.000000" in input_file(config, tmp_path)


@pytest.mark.parametrize(
    "compute",
    [COMPUTE_STAT(), COMPUTE_STAT(times=NONSTATIONARY()), COMPUTE_NONSTAT()],
    ids=["stationary", "stationary-series", "nonstationary"],
)
def test_stationary_mode_rejects_timed_computations(compute):
    with pytest.raises(ValidationError, match="lockup.compute=COMPUTE()"):
        SwanConfig(cgrid=CGRID, lockup=LOCKUP(compute=compute))


def test_nonstationary_mode_rejects_compute():
    with pytest.raises(ValidationError, match="single computation of stationary"):
        SwanConfig(
            cgrid=CGRID,
            startup=STARTUP(mode=MODE(kind="nonstationary")),
            lockup=LOCKUP(compute=COMPUTE()),
        )


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
    config = SwanConfig(cgrid=CGRID, output=output, lockup=LOCKUP(compute=COMPUTE()))
    assert "tbegblk" not in input_file(config, tmp_path)


def test_stationary_mode_rejects_output_times():
    from rompy_swan.components.group import OUTPUT
    from rompy_swan.components.output import BLOCK

    block = BLOCK(
        sname="COMPGRID", fname="grid.nc", output=["hsign"], times=dict(delt="PT1H")
    )
    with pytest.raises(ValidationError, match="output components with times"):
        SwanConfig(cgrid=CGRID, output=OUTPUT(block=block))


def test_blocks_get_output_times(tmp_path):
    from rompy_swan.components.group import OUTPUT
    from rompy_swan.components.output import BLOCK, BLOCKS

    blocks = BLOCKS(
        components=[
            BLOCK(sname="COMPGRID", fname="a.nc", output=["hsign"]),
            BLOCK(sname="COMPGRID", fname="b.nc", output=["dir"]),
        ]
    )
    config = SwanConfig(
        cgrid=CGRID,
        startup=STARTUP(mode=MODE(kind="nonstationary")),
        output=OUTPUT(block=blocks),
        lockup=LOCKUP(compute=COMPUTE_NONSTAT()),
    )
    assert input_file(config, tmp_path).count("OUTPUT tbegblk=20230101.000000") == 2


def test_output_interval_follows_the_run_period(tmp_path):
    from datetime import timedelta

    from rompy_swan.components.group import OUTPUT
    from rompy_swan.components.output import BLOCK
    from rompy_swan.subcomponents.time import TimeRangeOpen

    def config(block):
        return SwanConfig(
            cgrid=CGRID,
            startup=STARTUP(mode=MODE(kind="nonstationary")),
            output=OUTPUT(block=block),
            lockup=LOCKUP(compute=COMPUTE_NONSTAT()),
        )

    def generate(block, run_id):
        period = TimeRange(start="2023-01-01T00", end="2023-01-01T01", interval="10m")
        run = ModelRun(
            run_id=run_id, period=period, output_dir=tmp_path, config=config(block)
        )
        run.generate()
        return (tmp_path / run_id / "INPUT").read_text()

    default = BLOCK(sname="COMPGRID", fname="a.nc", output=["hsign"])
    assert "deltblk=600.0 SEC" in generate(default, "default")
    every_3h = BLOCK(
        sname="COMPGRID",
        fname="a.nc",
        output=["hsign"],
        times=TimeRangeOpen(delt=timedelta(hours=3)),
    )
    assert "deltblk=10800.0 SEC" in generate(every_3h, "every_3h")
