"""Test transmission models (private field types for OBSTACLE component)."""

import pytest
from pydantic import ValidationError

from rompy_swan.components.physics._transmission import (
    DANGREMOND,
    GODA,
    TRANS1D,
    TRANS2D,
    TRANSM,
)


def test_transm():
    trans = TRANSM()
    assert trans.render() == "TRANSM"
    trans = TRANSM(trcoef=0.0)
    assert trans.render() == "TRANSM trcoef=0.0"
    with pytest.raises(ValidationError):
        TRANSM(trcoef=1.1)


def test_trans1d():
    trans = TRANS1D(trcoef=[0.0, 0.0, 0.3, 0.2])
    assert trans.render() == "TRANS1D 0.0 0.0 0.3 0.2"
    with pytest.raises(ValidationError):
        TRANS1D(trcoef=[1.1, 0.0, 0.3, 0.2, 0.1])


def test_trans2d():
    trans = TRANS2D(trcoef=[[0.0, 0.0, 0.0], [0.1, 0.1, 0.1]])
    assert "TRANS2D" in trans.render()
    "0.0 0.0 0.0" in trans.render()
    "0.1 0.1 0.1" in trans.render()
    with pytest.raises(ValidationError):
        TRANS2D(trcoef=[[0.0, 0.0, 0.0], [0.1, 0.1, 0.1, 0.1]])
    with pytest.raises(ValidationError):
        TRANS2D(trcoef=[[0.0, 0.0, 0.0], [0.1, 0.1, 1.1]])


def test_goda():
    trans = GODA(hgt=1.0)
    assert trans.render() == "DAM GODA hgt=1.0"
    trans = GODA(hgt=-1.0, alpha=2.6, beta=0.15)
    assert trans.render() == "DAM GODA hgt=-1.0 alpha=2.6 beta=0.15"


def test_dangremond():
    trans = DANGREMOND(hgt=3.0, slope=60, Bk=10.0)
    assert trans.render() == "DAM DANGREMOND hgt=3.0 slope=60.0 Bk=10.0"
    with pytest.raises(ValidationError):
        DANGREMOND(hgt=3.0, slope=120, Bk=1.0)
