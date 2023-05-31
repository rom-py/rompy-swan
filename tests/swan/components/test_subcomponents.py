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
