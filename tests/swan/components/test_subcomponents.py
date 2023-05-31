"""Test subcomponents."""
import pytest
from pydantic import ValidationError

from rompy.swan.components.subcomponents import PAR, SIDE, SEGMENTXY, SEGMENTIJ


def test_side():
    SIDE(side="north")
    with pytest.raises(ValidationError):
        SIDE(side="nnw")


def test_segment_xy():
    SEGMENTXY(points=((0, 0), (1, 1), (2, 2)))
    with pytest.raises(ValidationError):
        SEGMENTXY(points=((0, 0, 0), (1, 1, 1), (2, 2, 2)))


def test_segment_ij():
    SEGMENTIJ(points=((0, 0), (1, 1), (2, 2)))
    with pytest.raises(ValidationError):
        SEGMENTIJ(points=((0, 0, 0), (1, 1, 1), (2, 2, 2)))


def test_par_constant():
    PAR(hs=1.0, per=10.0, dir=0.0, dd=0.0)


def test_par_variable():
    PAR(hs=[1.0, 1.0], per=[10.0, 10.0], dir=[0.0, 0.0], dd=[0.0, 0.0], dist=[0, 1])


def test_par_all_float_if_not_dist():
    with pytest.raises(ValidationError):
        PAR(hs=1.0, per=10.0, dir=0.0, dd=[0.0, 0.0])


def test_par_all_list_if_dist():
    with pytest.raises(ValidationError):
        PAR(hs=1.0, per=10.0, dir=0.0, dd=0.0, dist=[0.0])


def test_par_all_same_size_if_dist():
    with pytest.raises(ValidationError):
        PAR(hs=[1.0], per=[10.0], dir=[0.0], dd=[0.0, 0.0], dist=[0.0])
