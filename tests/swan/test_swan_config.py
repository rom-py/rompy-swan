"""Test swan_config class."""
import pytest
import logging
from rompy.swan.config import SwanConfigPydantic as SwanConfig
from rompy.swan.config import cgrid, inpgrid


logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def cgrid_instance():
    inst = cgrid.REGULAR(
        mdc=36,
        flow=0.04,
        fhigh=0.4,
        xlenc=100.0,
        ylenc=100.0,
        mxc=10,
        myc=10,
    )
    yield inst


@pytest.fixture(scope="module")
def inpgrid_instance():
    inst = inpgrid.REGULAR(
        inpgrid="BOTTOM",
        xpinp=0.0,
        ypinp=0.0,
        alpinp=0.0,
        mxinp=10,
        myinp=10,
        dxinp=0.1,
        dyinp=0.1,
    )
    yield inst


def test_swan_config_from_objects(cgrid_instance, inpgrid_instance):
    sc = SwanConfig(
        cgrid=cgrid_instance,
        inpgrid=inpgrid_instance,
    )
    sc._write_cmd()


def test_swan_config_from_dict(cgrid_instance, inpgrid_instance):
    cg = {k: v for k, v in cgrid_instance.dict().items() if k is not None}
    ig = {k: v for k, v in inpgrid_instance.dict().items() if k is not None}
    sc = SwanConfig(
        cgrid=cg,
        inpgrid=ig,
    )
    sc._write_cmd()
