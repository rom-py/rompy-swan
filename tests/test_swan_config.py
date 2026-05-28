"""Tests for SwanConfig.forcing field."""

import pytest

# Import test utilities
from test_utils.logging import get_test_logger

logger = get_test_logger(__name__)

from rompy_swan.components.cgrid import REGULAR as CGRID_REGULAR
from rompy_swan.components.group import LOCKUP
from rompy_swan.components.inpgrid import ICE, WIND
from rompy_swan.config import SwanConfig
from rompy_swan.subcomponents.readgrid import GRIDREGULAR
from rompy_swan.subcomponents.spectrum import SPECTRUM


@pytest.fixture(scope="module")
def cgrid():
    return CGRID_REGULAR(
        spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=0.4),
        grid=GRIDREGULAR(xp=0.0, yp=0.0, alp=0.0, xlen=1.0, ylen=1.0, mx=10, my=10),
    )


@pytest.fixture(scope="module")
def lockup():
    return LOCKUP(compute=dict(model_type="stat"))


@pytest.fixture(scope="module")
def wind():
    return WIND(vel=10.0, dir=270.0)


@pytest.fixture(scope="module")
def ice():
    return ICE(aice=0.5, hice=1.5)


def test_forcing_wind(cgrid, wind):
    config = SwanConfig(cgrid=cgrid, forcing=[wind])
    assert len(config.forcing) == 1
    assert isinstance(config.forcing[0], WIND)
    assert config.forcing[0].vel == 10.0
    assert config.forcing[0].dir == 270.0


def test_forcing_ice(cgrid, ice):
    config = SwanConfig(cgrid=cgrid, forcing=[ice])
    assert len(config.forcing) == 1
    assert isinstance(config.forcing[0], ICE)
    assert config.forcing[0].aice == 0.5
    assert config.forcing[0].hice == 1.5


def test_forcing_multiple(cgrid, wind, ice):
    config = SwanConfig(cgrid=cgrid, forcing=[wind, ice])
    assert len(config.forcing) == 2
    assert isinstance(config.forcing[0], WIND)
    assert isinstance(config.forcing[1], ICE)


def test_forcing_from_dict(cgrid):
    config = SwanConfig(
        cgrid=cgrid,
        forcing=[
            {"model_type": "wind", "vel": 15.0, "dir": 90.0},
            {"model_type": "ice", "aice": 0.3, "hice": 1.0},
        ],
    )
    assert len(config.forcing) == 2
    assert isinstance(config.forcing[0], WIND)
    assert config.forcing[0].vel == 15.0
    assert isinstance(config.forcing[1], ICE)


def test_forcing_none_by_default(cgrid):
    config = SwanConfig(cgrid=cgrid)
    assert config.forcing is None


def test_forcing_render_in_call(cgrid, wind, lockup, tmpdir):
    """forcing items appear in the rendered INPUT file."""
    from rompy.model import ModelRun

    config = SwanConfig(cgrid=cgrid, forcing=[wind], lockup=lockup)
    model = ModelRun(
        run_id="test",
        period=dict(start="20230101T00", duration="12h", interval="1h"),
        output_dir=str(tmpdir),
        config=config,
    )
    model.generate()

    input_file = tmpdir.join("test", "INPUT")
    content = input_file.read()
    logger.info(content)
    assert "WIND vel=10.0 dir=270.0" in content


def test_forcing_and_inpgrid_coexist(cgrid, wind, lockup, tmpdir):
    """forcing and inpgrid can be specified together."""
    from rompy.model import ModelRun
    from rompy_swan.components.group import INPGRIDS
    from rompy_swan.components.inpgrid import READINP
    from rompy_swan.components.inpgrid import REGULAR as INPGRID_REGULAR

    inpgrid = INPGRIDS(
        inpgrids=[
            INPGRID_REGULAR(
                grid_type="bottom",
                xpinp=0.0,
                ypinp=0.0,
                alpinp=0.0,
                mxinp=10,
                myinp=10,
                dxinp=0.1,
                dyinp=0.1,
                excval=-999.0,
                readinp=READINP(fname1="bottom.txt"),
            )
        ]
    )
    config = SwanConfig(cgrid=cgrid, inpgrid=inpgrid, forcing=[wind], lockup=lockup)
    model = ModelRun(
        run_id="test",
        period=dict(start="20230101T00", duration="12h", interval="1h"),
        output_dir=str(tmpdir),
        config=config,
    )
    model.generate()

    input_file = tmpdir.join("test", "INPUT")
    content = input_file.read()
    assert "INPGRID BOTTOM" in content
    assert "WIND vel=10.0 dir=270.0" in content
