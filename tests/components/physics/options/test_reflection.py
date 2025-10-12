"""Test reflection option types for OBSTACLE component."""

import pytest
from pydantic import ValidationError

from rompy_swan.components.physics.options.reflection import FREEBOARD, LINE, RDIFF, REFL, RSPEC


def test_refl():
    refl = REFL()
    assert refl.render() == "REFL"
    refl = REFL(reflc=0.5)
    assert refl.render() == "REFL reflc=0.5"


def test_rspec():
    refl = RSPEC()
    assert refl.render() == "RSPEC"


def test_rdiff():
    refl = RDIFF()
    assert refl.render() == "RDIFF"
    refl = RDIFF(pown=1.0)
    assert refl.render() == "RDIFF pown=1.0"


def test_freeboard():
    free = FREEBOARD(
        hgt=2.0,
        gammat=0.5,
        gammar=0.5,
        quay=True,
    )
    assert free.render() == "FREEBOARD hgt=2.0 gammat=0.5 gammar=0.5 QUAY"


def test_freeboard_no_quay():
    free = FREEBOARD(
        hgt=2.0,
        gammat=0.5,
        gammar=0.5,
        quay=False,
    )
    assert free.render() == "FREEBOARD hgt=2.0 gammat=0.5 gammar=0.5"


def test_freeboard_gamma_gt_0():
    with pytest.raises(ValidationError):
        FREEBOARD(hgt=2.0, gammat=0.0)
    with pytest.raises(ValidationError):
        FREEBOARD(hgt=2.0, gammar=0.0)


def test_line():
    line = LINE(xp=[174.1, 174.2, 174.3], yp=[-39.1, -39.1, -39.1])
    assert [f"{x} {y}" in line.render() for x, y in zip(line.xp, line.yp)]
