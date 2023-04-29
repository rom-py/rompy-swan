"""Test swan_config class."""
import pytest
import logging
from rompy.swan.config import SwanConfigPydantic as SwanConfig
from rompy.swan.config import cgrid, inpgrid


logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def cgrid_instance():
    inst = cgrid.CGridRegular(
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
    inst = inpgrid.InpGrid(
        mdc=36,
        flow=0.04,
        fhigh=0.4,
        xlenc=100.0,
        ylenc=100.0,
        mxc=10,
        myc=10,
    )
    yield inst


def test_swan_config(cgrid_instance, inpgrid_instance):
    sc = SwanConfig(
        cgrid=cgrid_instance,
        inpgrid=inpgrid_instance,
    )
    sc._write_cmd()
