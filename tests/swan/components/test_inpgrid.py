"""Test inpgrid component."""
import pytest
import logging
from pydantic import ValidationError

from rompy.swan.components.inpgrid import (
    INPGRID,
    REGULAR,
    CURVILINEAR,
    UNSTRUCTURED,
    InpgridOptions,
    NONSTATIONARY,
)


logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def inpgrid_instance():
    inst = REGULAR(
        inpgrid="BOTTOM",
        xpinp=0.0,
        ypinp=0.0,
        alpinp=0.0,
        mxinp=10,
        myinp=10,
        dxinp=0.1,
        dyinp=0.1,
        excval=-999.0,
    )


def test_valid_inpgrid_options():
    for inpgrid in InpgridOptions:
        INPGRID(inpgrid=inpgrid.value)
        INPGRID(inpgrid=inpgrid.value.lower())
        INPGRID(inpgrid=inpgrid.value.upper())
    with pytest.raises(ValidationError):
        INPGRID(inpgrid="invalid")


def test_excval():
    inpgrid = INPGRID(inpgrid="BOTTOM", excval=-999)
    assert inpgrid.excval == -999.0
    assert isinstance(inpgrid.excval, float)


def test_nonstationary():
    inpgrid = INPGRID(
        inpgrid="BOTTOM",
        nonstationary=NONSTATIONARY(
            tbeg="2023-01-01T00:00:00",
            delt="PT30M",
            tend="2023-02-01T00:00:00",
            deltfmt="hr",
        )
    )
    assert isinstance(inpgrid.nonstationary, NONSTATIONARY)
    assert inpgrid.nonstationary.suffix == "inp"


def test_inpgrid_regular():
    inpgrid = REGULAR(
        inpgrid=InpgridOptions.bottom,
        xpinp=0.0,
        ypinp=0.0,
        alpinp=0.0,
        mxinp=10,
        myinp=10,
        dxinp=0.1,
        dyinp=0.1,
        excval=-999.0,
    )
    logger.info(inpgrid.render())
