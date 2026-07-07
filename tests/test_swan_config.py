"""Tests for SwanConfig validators."""

import pytest

# Import test utilities
from test_utils.logging import get_test_logger

logger = get_test_logger(__name__)

from rompy_swan.components.cgrid import REGULAR as CGRID_REGULAR
from rompy_swan.components.group import FORCING, LOCKUP
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


def test_forcing_wind_only(cgrid, wind):
    config = SwanConfig(cgrid=cgrid, forcing=FORCING(wind=wind))
    assert isinstance(config.forcing.wind, WIND)
    assert config.forcing.wind.vel == 10.0
    assert config.forcing.wind.dir == 270.0
    assert config.forcing.ice is None


def test_forcing_ice_only(cgrid, ice):
    config = SwanConfig(cgrid=cgrid, forcing=FORCING(ice=ice))
    assert isinstance(config.forcing.ice, ICE)
    assert config.forcing.ice.aice == 0.5
    assert config.forcing.ice.hice == 1.5
    assert config.forcing.wind is None


def test_forcing_wind_and_ice(cgrid, wind, ice):
    config = SwanConfig(cgrid=cgrid, forcing=FORCING(wind=wind, ice=ice))
    assert isinstance(config.forcing.wind, WIND)
    assert isinstance(config.forcing.ice, ICE)


def test_forcing_requires_at_least_one(cgrid):
    with pytest.raises(Exception):
        SwanConfig(cgrid=cgrid, forcing=FORCING())


def test_forcing_from_dict(cgrid):
    config = SwanConfig(
        cgrid=cgrid,
        forcing={"wind": {"vel": 15.0, "dir": 90.0}, "ice": {"aice": 0.3, "hice": 1.0}},
    )
    assert isinstance(config.forcing.wind, WIND)
    assert config.forcing.wind.vel == 15.0
    assert isinstance(config.forcing.ice, ICE)


def test_forcing_none_by_default(cgrid):
    config = SwanConfig(cgrid=cgrid)
    assert config.forcing is None


def test_forcing_render_in_call(cgrid, wind, lockup, tmpdir):
    """forcing items appear in the rendered INPUT file."""
    from rompy.model import ModelRun

    config = SwanConfig(cgrid=cgrid, forcing=FORCING(wind=wind), lockup=lockup)
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
    config = SwanConfig(cgrid=cgrid, inpgrid=inpgrid, forcing=FORCING(wind=wind), lockup=lockup)
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


# ── SEGMENT IJ sentinel (-1) resolution ──────────────────────────────────────


def test_segment_ij_sentinel_resolved(cgrid):
    """BOUNDSPEC SEGMENT IJ: -1 is replaced by the cgrid max index (mx/my)."""
    config = SwanConfig(
        cgrid=cgrid,
        boundary=dict(
            model_type="boundspec",
            location=dict(
                model_type="segment",
                points=dict(model_type="ij", i=[0, -1, -1], j=[-1, -1, 0]),
            ),
            data=dict(model_type="constantpar", hs=2.0, per=12.0, dir=270.0, dd=25.0),
        ),
    )
    pts = config.boundary.location.points
    mx = cgrid.grid.mx
    my = cgrid.grid.my
    assert -1 not in pts.i
    assert -1 not in pts.j
    assert pts.i == [0, mx, mx]
    assert pts.j == [my, my, 0]


def test_segment_ij_no_sentinel_unchanged(cgrid):
    """BOUNDSPEC SEGMENT IJ without -1 is passed through unchanged."""
    config = SwanConfig(
        cgrid=cgrid,
        boundary=dict(
            model_type="boundspec",
            location=dict(
                model_type="segment",
                points=dict(model_type="ij", i=[0, 10, 10], j=[10, 10, 0]),
            ),
            data=dict(model_type="constantpar", hs=2.0, per=12.0, dir=270.0, dd=25.0),
        ),
    )
    pts = config.boundary.location.points
    assert pts.i == [0, 10, 10]
    assert pts.j == [10, 10, 0]


def test_segment_ij_sentinel_renders_correctly(cgrid, lockup, tmpdir):
    """Resolved SEGMENT IJ sentinel values appear correctly in the INPUT file."""
    from rompy.model import ModelRun

    config = SwanConfig(
        cgrid=cgrid,
        boundary=dict(
            model_type="boundspec",
            location=dict(
                model_type="segment",
                points=dict(model_type="ij", i=[0, -1, -1], j=[-1, -1, 0]),
            ),
            data=dict(model_type="constantpar", hs=2.0, per=12.0, dir=270.0, dd=25.0),
        ),
        lockup=lockup,
    )
    model = ModelRun(
        run_id="test",
        period=dict(start="20230101T00", duration="12h", interval="1h"),
        output_dir=str(tmpdir),
        config=config,
    )
    model.generate()

    content = tmpdir.join("test", "INPUT").read()
    mx = cgrid.grid.mx
    my = cgrid.grid.my
    assert f"i=0 j={my}" in content
    assert f"i={mx} j={my}" in content
    assert f"i={mx} j=0" in content
    assert "i=-1" not in content
    assert "j=-1" not in content
