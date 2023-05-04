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
    inst_wind = inpgrid.REGULAR(
        inpgrid="WIND",
        xpinp=0.0,
        ypinp=0.0,
        alpinp=0.0,
        mxinp=10,
        myinp=10,
        dxinp=0.1,
        dyinp=0.1,
        excval=-999.0,
        nonstationary=inpgrid.NONSTATIONARY(
            tbeg="2023-01-01T00:00:00",
            delt="PT30M",
            tend="2023-02-01T00:00:00",
            deltfmt="hr",
        )
    )
    inst_bottom = inst_wind.copy()
    inst_bottom.inpgrid = "BOTTOM"
    inst_bottom.nonstationary = None
    yield [inst_bottom, inst_wind]


def test_swan_config_from_objects(cgrid_instance, inpgrid_instance):
    sc = SwanConfig(
        cgrid=cgrid_instance,
        inpgrid=inpgrid_instance,
    )
    sc._write_cmd()


def test_swan_config_from_dict(cgrid_instance, inpgrid_instance):
    cgrid_dict = {
        "kind": "regular",
        "mdc": 36,
        "flow": 0.04,
        "fhigh": 0.4,
        "xlenc": 100.0,
        "ylenc": 100.0,
        "mxc": 10,
        "myc": 10,
    }
    inpgrid_wind_dict = {
        "kind": "regular",
        "inpgrid": "wind",
        "xpinp": 0.0,
        "ypinp": 0.0,
        "alpinp": 0.0,
        "mxinp": 10,
        "myinp": 10,
        "dxinp": 0.1,
        "dyinp": 0.1,
        "excval": -999.0,
        "nonstationary": {
            "tbeg": "2023-01-01T00:00:00",
            "delt": "PT30M",
            "tend": "2023-02-01T00:00:00",
            "deltfmt": "hr",
        },
    }
    sc = SwanConfig(
        cgrid=cgrid_dict,
        inpgrid=[inpgrid_wind_dict],
    )
    sc._write_cmd()
