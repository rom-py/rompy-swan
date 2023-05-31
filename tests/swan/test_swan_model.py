"""Test swan_config class."""
import pytest
import logging

from rompy.core.model import BaseModel
from rompy.swan.config import SwanConfigPydantic as SwanConfig


logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def cgrid_dict():
    inst = dict(
        model_type="regular",
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
def inpgrid_dict():
    inst_bottom = dict(
        model_type="regular",
        grid_type="BOTTOM",
        xpinp=0.0,
        ypinp=0.0,
        alpinp=0.0,
        mxinp=10,
        myinp=10,
        dxinp=0.1,
        dyinp=0.1,
        excval=-999.0,
        readinp=dict(
            model_type="readinp",
            fname1="bottom.txt",
        ),
    )
    inst_wind = inst_bottom.copy()
    inst_wind["grid_type"] = "WIND"
    inst_wind["nonstationary"] = dict(
        tbeg="2023-01-01T00:00:00",
        delt="PT30M",
        tend="2023-02-01T00:00:00",
        deltfmt="hr",
    )
    inst_wind["readinp"] = dict(
        model_type="readinp",
        fname1="wind.txt",
    )
    yield [inst_bottom, inst_wind]


@pytest.fixture(scope="module")
def boundary_dict():
    inst = dict(
        model_type="boundspec",
        location=dict(
            model_type="segmentxy",
            points=[(0, 0), (1, 1), (2, 2)],
        ),
    )
    yield inst


def test_swan_model(tmpdir, cgrid_dict, inpgrid_dict, boundary_dict):
    config = SwanConfig(
        cgrid=cgrid_dict,
        inpgrid=inpgrid_dict,
        boundary=boundary_dict,
    )
    model = BaseModel(
        run_id="test",
        output_dir=str(tmpdir),
        config=config,
        template="/source/csiro/rompy/rompy/templates/swan2",
    )
    # import ipdb; ipdb.set_trace()
    model.generate()
    # sc.render_cmd()
