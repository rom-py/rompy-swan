"""Test startup components."""
import pytest
from pydantic import ValidationError

from rompy.swan.components.physics import GEN1, GEN2, GEN3, DCTA, LTA, SPB, VEGETATION


# =====================================================================================
# GEN
# =====================================================================================
def test_gen1_default():
    phys = GEN1()
    assert phys.render() == "GEN1"


def test_gen1_set_all():
    phys = GEN1(
        cf10=188,
        cf20=0.59,
        cf30=0.12,
        cf40=250,
        edmlpm=0.0036,
        cdrag=0.0012,
        umin=1,
        cfpm=0.13,
    )
    assert phys.render() == (
        "GEN1 cf10=188.0 cf20=0.59 cf30=0.12 cf40=250.0 edmlpm=0.0036 cdrag=0.0012 "
        "umin=1.0 cfpm=0.13"
    )


def test_gen2_default():
    phys = GEN2()
    assert phys.render() == "GEN2"


def test_gen2_set_all():
    phys = GEN2(
        cf10=188,
        cf20=0.59,
        cf30=0.12,
        cf40=250,
        cf50=0.0023,
        cf60=-0.223,
        edmlpm=0.0036,
        cdrag=0.0012,
        umin=1,
        cfpm=0.13,
    )
    assert phys.render() == (
        "GEN2 cf10=188.0 cf20=0.59 cf30=0.12 cf40=250.0 cf50=0.0023 cf60=-0.223 "
        "edmlpm=0.0036 cdrag=0.0012 umin=1.0 cfpm=0.13"
    )


def test_gen3_default():
    phys = GEN3()
    assert phys.render() == f"GEN3 {phys.source_terms.render()}"


# =====================================================================================
# TRIADS
# =====================================================================================
def test_triad_dcta():
    phys = DCTA()
    assert phys.render() == "TRIAD DCTA COLL BIPHASE ELDEBERKY"
    phys = DCTA(
        biphase=dict(model_type="dewit", lpar=0.0), trfac=4.4, p=1.3, noncolinear=True
    )
    assert phys.render() == "TRIAD DCTA trfac=4.4 p=1.3 NONC BIPHASE DEWIT lpar=0.0"


def test_triad_lta():
    phys = LTA()
    assert phys.render() == "TRIAD LTA BIPHASE ELDEBERKY"
    phys = LTA(biphase=dict(model_type="dewit", lpar=0.0), trfac=0.8, cutfr=2.5)
    assert phys.render() == "TRIAD LTA trfac=0.8 cutfr=2.5 BIPHASE DEWIT lpar=0.0"


def test_triad_spb():
    phys = SPB()
    assert phys.render() == "TRIAD SPB BIPHASE ELDEBERKY"
    phys = SPB(biphase=dict(model_type="dewit", lpar=0.0), trfac=0.9, a=0.95, b=0.0)
    assert phys.render() == "TRIAD SPB trfac=0.9 a=0.95 b=0.0 BIPHASE DEWIT lpar=0.0"


# =====================================================================================
# VEGETATION
# =====================================================================================
def test_vegetation():
    vegetation = VEGETATION(
        height=1.0,
        diamtr=0.1,
        drag=0.1,
    )
    assert vegetation.render() == (
        "VEGETATION iveg=1 height=1.0 diamtr=0.1 nstems=1 drag=0.1"
    )


def test_vegetation_number_of_layers():
    layers = 3
    v = VEGETATION(
        height=[1.0] * layers,
        diamtr=[0.1] * layers,
        drag=[0.1] * layers,
        nstems=[2] * layers,
    )
    assert v.render().count("height") == layers


def test_vegetation_number_of_layers_mismatch():
    with pytest.raises(ValidationError):
        VEGETATION(
            height=1.0,
            diamtr=[0.1, 0.1],
            drag=[0.1],
            nstems=[2, 2, 2],
        )
