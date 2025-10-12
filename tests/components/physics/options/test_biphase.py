"""Test biphase option types for TRIAD component."""


from rompy_swan.components.physics.options.biphase import DEWIT, ELDEBERKY


def test_biphase_elderberky():
    biphase = ELDEBERKY()
    assert biphase.render() == "BIPHASE ELDEBERKY"
    biphase = ELDEBERKY(urcrit=0.63)
    assert biphase.render() == "BIPHASE ELDEBERKY urcrit=0.63"


def test_biphase_dewit():
    biphase = DEWIT()
    assert biphase.render() == "BIPHASE DEWIT"
    biphase = DEWIT(lpar=0)
    assert biphase.render() == "BIPHASE DEWIT lpar=0.0"
