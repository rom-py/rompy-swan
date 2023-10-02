"""Test lockup components."""
import pytest
from pydantic import ValidationError

from rompy.swan.subcomponents.time import NONSTATIONARY
from rompy.swan.components.lockup import (
    COMPUTE, HOTFILE, STOP, COMPUTE_HOTFILE, LOCKUP,
)


@pytest.fixture(scope="module")
def times():
    yield NONSTATIONARY(
        tbeg=dict(time="1990-01-01T00:00:00", tfmt=1),
        tend=dict(time="1990-02-01T00:00:00", tfmt=1),
        delt=dict(delt="PT1H", dfmt="hr"),
    )


def test_compute():
    comp = COMPUTE()
    assert comp.render() == "COMPUTE"


def test_compute_stationary():
    comp = COMPUTE(
        times=dict(model_type="stationary", time=dict(time="1990-01-01T00:00:00")),
    )
    assert comp.render() == "COMPUTE STATIONARY time=19900101.000000"


def test_compute_nonstationary(times):
    comp = COMPUTE(times=times)
    assert comp.render() == (
        "COMPUTE NONSTATIONARY tbegc=19900101.000000 deltc=1.0 HR "
        "tendc=19900201.000000"
    )


def test_hotfile_default():
    hotfile = HOTFILE(fname="hotfile")
    assert hotfile.render() == "HOTFILE fname='hotfile'"


def test_hotfile_unformatted():
    hotfile = HOTFILE(fname="hotfile", format="unformatted")
    assert hotfile.render() == "HOTFILE fname='hotfile' UNFORMATTED"


def test_stop():
    stop = STOP()
    assert stop.render() == "STOP"


def test_compute_hotfile(times):
    comphot = COMPUTE_HOTFILE(times=times, fname="hotfile")
    l1, l2 = comphot.render().split("\n")
    assert l1 == (
        "COMPUTE NONSTATIONARY tbegc=19900101.000000 deltc=1.0 HR "
        "tendc=19900201.000000"
    )
    assert l2 == "HOTFILE fname='hotfile-19900201T000000'"


def test_lockup_compute_nohotfile(times):
    compute = dict(model_type="compute", times=times)
    lockup = LOCKUP(compute=[compute])
    assert not hasattr(lockup.compute[0], "fname")


def test_lockup_compute_hotfile_separated(times):
    compute = dict(model_type="compute", times=times)
    hotfile = dict(fname="hotfile", format="free")
    lockup = LOCKUP(compute=[compute], hotfile=hotfile)
    assert lockup.hotfile is not None


def test_lockup_compute_hotfile_grouped(times):
    compute = dict(model_type="compute_hotfile", times=times, fname="hotfile")
    lockup = LOCKUP(compute=[compute])
    assert hasattr(lockup.compute[0], "fname")


def test_lockup_hotfile_defined_only_once(times):
    compute = dict(model_type="compute_hotfile", times=times, fname="hotfile")
    hotfile = dict(fname="hotfile", format="free")
    with pytest.raises(ValidationError):
        LOCKUP(compute=[compute], hotfile=hotfile)
