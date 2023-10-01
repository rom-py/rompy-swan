"""Test time sub-component."""
import pytest
from datetime import datetime, timedelta

from rompy.swan.subcomponents.time import (
    TIME,
    DELT,
    TIMERANGE,
    STATIONARY,
    NONSTATIONARY,
)


@pytest.mark.parametrize(
    "tfmt, tmpl",
    [
        (1, "%Y%m%d.%H%M%S"),
        (2, "'%d-%b-%y %H:%M:%S'"),
        (3, "%m/%d/%y.%H:%M:%S"),
        (4, "%H:%M:%S"),
        (5, "%y/%m/%d %H:%M:%S'"),
        (6, "%y%m%d%H%M"),
    ],
)
def test_time(tfmt, tmpl):
    t = datetime(1990, 1, 1, 0, 0, 0)
    time = TIME(time=t, tfmt=tfmt)
    assert time.render() == t.strftime(tmpl)


@pytest.mark.parametrize(
    "delt, dfmt, rendered",
    [
        (1800, "sec", "1800.0 SEC"),
        (timedelta(hours=2), "min", "120.0 MIN"),
        ("PT60M", "hr", "1.0 HR"),
    ],
)
def test_delt(delt, dfmt, rendered):
    delta = DELT(delt=delt, dfmt=dfmt)
    assert delta.render() == rendered


def test_timerange():
    tr = TIMERANGE(
        tbeg=dict(time="2023-01-01T00:00:00"),
        delt=dict(delt="PT30M", dfmt="min"),
        tend=dict(time="2023-02-01T00:00:00"),
    )
    assert tr.render() == "tbeg=20230101.000000 delt=30.0 MIN tend=20230201.000000"


def test_nonstationary():
    tr = NONSTATIONARY(
        tbeg=dict(time="2023-01-01T00:00:00", tfmt=6),
        delt=dict(delt="PT30M", dfmt="sec"),
        tend=dict(time="2023-02-01T00:00:00", tfmt=6),
        suffix="tbl",
    )
    assert tr.render() == (
        "NONSTATIONARY tbegtbl=2301010000 delttbl=1800.0 SEC tendtbl=2302010000"
    )


def test_stationary():
    stat = STATIONARY(time=dict(time="2023-01-01T00:00:00", tfmt=1))
    assert stat.render() == "STATIONARY time=20230101.000000"
