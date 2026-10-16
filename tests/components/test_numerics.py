"""Test numerics components."""

from rompy_swan.components.numerics import NUMERIC
from rompy_swan.subcomponents.numerics import CSIGMA, SETUP


def test_numeric_renders_csigma_and_setup():
    numeric = NUMERIC(csigma=CSIGMA(cfl=0.9), setup=SETUP(eps2=1e-4))
    rendered = numeric.render()
    assert "CSIGMA" in rendered
    assert "SETUP" in rendered


def test_csigma_model_type():
    assert CSIGMA().model_type == "csigma"
