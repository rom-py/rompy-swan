"""Test SWAN boundary components."""
import pytest

from rompy.swan.components.boundary import BOUNDSPEC, BOUNDNEST1
from rompy.swan.subcomponents.shape import SHAPESPEC, JONSWAP
from rompy.swan.subcomponents.boundary import SIDE, CONSTANTPAR


def test_boundspec():
    bnd = BOUNDSPEC(
        shapespec=SHAPESPEC(
            shape=JONSWAP(
                gamma=3.3
            ),
            per_type="peak",
            dspr_type="power",
        ),
        location=SIDE(
            side="west",
        ),
        data=CONSTANTPAR(
            hs=1.0,
            per=10.0,
            dir=0.0,
            dd=10.0,
        ),
    )
    assert "BOUND SHAPESPEC JONSWAP gamma=3.3 PEAK DSPR POWER" in bnd.render()
    assert "BOUNDSPEC SIDE WEST CCW CONSTANT PAR hs=1.0" in bnd.render()


def test_boundnest1():
    bnd = BOUNDNEST1(fname="boundary.txt")
    assert bnd.render() == "BOUNDNEST1 NEST fname='boundary.txt' CLOSED"
