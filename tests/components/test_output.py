"""Test output components."""

import copy

import pytest

# Import test utilities
from test_utils.logging import get_test_logger

# Initialize logger
logger = get_test_logger(__name__)

import numpy as np
from pydantic import ValidationError

from rompy_swan.components.group import OUTPUT
from rompy_swan.components.output import (
    BLOCK,
    BLOCKS,
    CURVE,
    CURVES,
    FRAME,
    GROUP,
    ISOLINE,
    NEST,
    NESTOUT,
    NGRID,
    NGRID_UNSTRUCTURED,
    OUTPUT_OPTIONS,
    POINTS,
    POINTS_FILE,
    QUANTITIES,
    QUANTITY,
    RAY,
    SPECIAL_NAMES,
    SPECOUT,
    TABLE,
    TEST,
    BaseLocation,
)
from rompy_swan.subcomponents.time import TimeRangeOpen


@pytest.fixture(scope="module")
def times():
    yield TimeRangeOpen(tbeg="1990-01-01T00:00:00", delt="PT1H", tfmt=1, dfmt="hr")


@pytest.fixture(scope="module")
def frame():
    yield FRAME(
        sname="outgrid",
        grid=dict(xp=173, yp=-40, xlen=2, ylen=2, mx=19, my=19),
    )


@pytest.fixture(scope="module")
def group():
    yield GROUP(sname="subgrid", ix1=20, iy1=0, ix2=50, iy2=100)


@pytest.fixture(scope="module")
def curve():
    yield CURVE(
        sname="curve1",
        xp1=172,
        yp1=-40,
        npts=[3, 3],
        xp=[172.0, 174.0],
        yp=[-38.0, -38.0],
    )


@pytest.fixture(scope="module")
def curves(curve):
    curve2 = copy.deepcopy(curve)
    curve2.sname = "curve2"
    yield CURVES(curves=[curve, curve2])


@pytest.fixture(scope="module")
def ray():
    yield RAY(
        rname="outray",
        xp1=171.9,
        yp1=-40.1,
        xq1=172.1,
        yq1=-39.9,
        npts=[3, 3],
        xp=[171.9, 173.9],
        yp=[-38.1, -38.1],
        xq=[172.1, 174.1],
        yq=[-37.9, -37.9],
    )


@pytest.fixture(scope="module")
def isoline():
    yield ISOLINE(sname="outcurve", rname="outray", dep_type="depth", dep=12.0)


@pytest.fixture(scope="module")
def points():
    yield POINTS(sname="outpts", xp=[172.3, 172.4], yp=[-39, -39])


@pytest.fixture(scope="module")
def ngrid():
    yield NGRID(
        sname="outnest", grid=dict(xp=173, yp=-40, xlen=2, ylen=2, mx=19, my=19)
    )


@pytest.fixture(scope="module")
def quantity():
    yield QUANTITY(output=["hsign", "tm02", "fspr"], fmin=0.03, fmax=0.5)


@pytest.fixture(scope="module")
def quantities():
    yield QUANTITIES(
        quantities=[
            QUANTITY(output=["hsign", "tm02", "fspr"], fmin=0.03, fmax=0.5),
            QUANTITY(output=["hswell"], fswell=0.125),
        ],
    )


@pytest.fixture(scope="module")
def output_options():
    yield OUTPUT_OPTIONS(comment="!", field=10, ndec_block=4, len=20, ndec_spec=6)


@pytest.fixture(scope="module")
def block(times):
    yield BLOCK(
        sname="COMPGRID",
        header=False,
        fname="./output-grid.nc",
        idla=3,
        output=["hsign", "hswell", "dir", "tps", "tm01", "watlev", "qp"],
        times=times,
    )


@pytest.fixture(scope="module")
def table(times):
    yield TABLE(
        sname="outpts",
        format="noheader",
        fname="./output_table.nc",
        output=["hsign", "hswell", "dir", "tps", "tm01", "watlev", "qp"],
        times=times,
    )


@pytest.fixture(scope="module")
def specout(times):
    yield SPECOUT(
        sname="outpts",
        dim=dict(model_type="spec2d"),
        freq=dict(model_type="rel"),
        fname="./specout.nc",
        times=times,
    )


@pytest.fixture(scope="module")
def nestout(times):
    yield NESTOUT(sname="outnest", fname="./nestout.swn", times=times)


@pytest.fixture(scope="module")
def nest(times):
    """Single nest fixture."""
    yield NEST(
        sname="child1",
        ngrid=dict(
            model_type="ngrid",
            grid=dict(xp=167.0, yp=-45.5, xlen=0.1, ylen=0.1, mx=12, my=14),
        ),
        nestout=dict(
            fname="nestout_child1.swn",
            times=times,
        ),
    )


@pytest.fixture(scope="module")
def nest_unstructured(times):
    """Nest fixture with unstructured grid."""
    yield NEST(
        sname="unstruct",
        ngrid=dict(
            model_type="ngrid_unstructured",
            kind="triangle",
            fname="ngrid.txt",
        ),
        nestout=dict(
            fname="nestout_unstruct.swn",
            times=times,
        ),
    )


@pytest.fixture(scope="module")
def test():
    yield TEST(
        points=dict(
            model_type="xy",
            x=np.linspace(172.5, 174.0, 25),
            y=25 * [-38],
        ),
        fname_s2d="2d_variance_density.test",
    )


def test_base_location():
    loc = BaseLocation(sname="outsites")
    assert loc.render() == "LOCATIONS sname='outsites'"


def test_sname_lt8():
    with pytest.raises(ValidationError):
        BaseLocation(sname="outputlocations")


@pytest.mark.parametrize("sname", SPECIAL_NAMES)
def test_sname_special(sname):
    with pytest.raises(ValidationError):
        BaseLocation(sname=sname)


def test_frame(frame):
    assert frame.render() == (
        "FRAME sname='outgrid' xpfr=173.0 ypfr=-40.0 alpfr=0.0 "
        "xlenfr=2.0 ylenfr=2.0 mxfr=19 myfr=19"
    )


def test_group(group):
    group.render() == "GROUP sname='subgrid' SUBGRID ix1=20 iy1=0 ix2=50 iy2=100"


def test_curve(curve):
    assert "CURVE sname='outcurve'" in curve.render()


def test_curve(curve):
    loc = CURVES(curves=[curve, curve])
    assert loc.render().count("CURVE sname=") == 2


def test_ray(ray):
    assert ray.render().startswith("RAY rname='outray'")


def test_isoline(isoline):
    assert isoline.render() == "ISOLINE sname='outcurve' rname='outray' DEPTH dep=12.0"


def test_points(points):
    assert points.render().startswith("POINTS sname='outpts' &")


def test_points_file():
    loc = POINTS_FILE(sname="outpts", fname="./output_points.nc")
    assert loc.render() == "POINTS sname='outpts' fname='./output_points.nc'"


def test_ngrid(ngrid):
    assert ngrid.render() == (
        "NGRID sname='outnest' xpn=173.0 ypn=-40.0 alpn=0.0 xlenn=2.0 ylenn=2.0 "
        "mxn=19 myn=19"
    )


def test_ngrid_unstructured():
    loc = NGRID_UNSTRUCTURED(sname="outnest", kind="triangle", fname="./ngrid.txt")
    assert loc.render() == (
        "NGRID sname='outnest' UNSTRUCTURED TRIANGLE fname='./ngrid.txt'"
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(output=["xp"], hexp=100),
        dict(output=["hsign", "tm01", "rtmm10"], excv=-9),
        dict(output=["hsign", "tm02", "fspr"], fmin=0.03, fmax=0.5),
        dict(output=["hsign"], fswell=0.08),
        dict(output=["per"], short="Tm-1,0", power=0),
        dict(output=["transp", "force"], coord="frame"),
    ],
)
def test_quantity(kwargs):
    QUANTITY(**kwargs)


def test_quantity_valid_output():
    with pytest.raises(ValidationError):
        QUANTITY(output=["hsign", "notvalid"])


def test_output_options(output_options):
    assert output_options.render() == (
        "OUTPUT OPTIONS comment='!' TABLE field=10 BLOCK ndec=4 len=20 SPEC ndec=6"
    )


def test_block():
    block = BLOCK(sname="outgrid", fname="./depth-frame.nc", output=["depth"])
    block.render() == "BLOCK sname='outgrid' fname='./depth-frame.nc' DEPTH"


def test_blocks():
    block1 = BLOCK(sname="outgrid", fname="./depth.txt", output=["depth"])
    block2 = BLOCK(
        sname="outgrid",
        fname="./output.nc",
        output=["hsign", "hswell", "tm01", "tps", "vel", "wind"],
    )
    blocks = BLOCKS(components=[block1, block2])
    assert len(blocks.components) == 2
    assert isinstance(blocks.components[0], BLOCK)


def test_block_nonstationary(block):
    assert "OUTPUT tbegblk=19900101.000000 deltblk=1.0 HR" in block.render()


def test_table(table):
    assert table.render().startswith(
        "TABLE sname='outpts' NOHEADER fname='./output_table.nc' &"
    )


def test_specout(specout):
    assert specout.render() == (
        "SPECOUT sname='outpts' SPEC2D REL fname='./specout.nc' "
        "OUTPUT tbegspc=19900101.000000 deltspc=1.0 HR"
    )


def test_nestout(nestout):
    assert nestout.render() == (
        "NESTOUT sname='outnest' fname='./nestout.swn' "
        "OUTPUT tbegnst=19900101.000000 deltnst=1.0 HR"
    )


def test_test_xy(test):
    assert test.render().startswith("TEST POINTS XY &")


def test_test_ij():
    test = TEST(
        itest=10,
        points=dict(model_type="ij", i=[0, 0], j=[10, 20]),
        fname_par="integral_parameters.test",
        fname_s1d="1d_variance_density.test",
        fname_s2d="2d_variance_density.test",
    )
    print(test.render())


def test_test_max50():
    with pytest.raises(ValidationError):
        TEST(
            points=dict(
                model_type="xy",
                x=np.linspace(172.5, 174.0, 60),
                y=60 * [-38],
            ),
            fname_s2d="2d_variance_density.test",
        )


def test_output_group_all_set(
    frame,
    group,
    curves,
    ray,
    isoline,
    points,
    ngrid,
    quantities,
    output_options,
    block,
    table,
    specout,
    nestout,
):
    """Test OUTPUT with all components using legacy ngrid/nestout fields."""
    output = OUTPUT(
        frame=frame,
        group=group,
        curve=curves,
        ray=ray,
        isoline=isoline,
        points=points,
        ngrid=ngrid,
        quantity=quantities,
        output_options=output_options,
        block=block,
        table=table,
        specout=specout,
        nestout=nestout,
    )
    print("")
    print(output.render())


def test_output_group_all_set_with_nests(
    frame,
    group,
    curves,
    ray,
    isoline,
    points,
    nest,
    quantities,
    output_options,
    block,
    table,
    specout,
):
    """Test OUTPUT with all components using new nests field."""
    output = OUTPUT(
        frame=frame,
        group=group,
        curve=curves,
        ray=ray,
        isoline=isoline,
        points=points,
        nests=[nest],
        quantity=quantities,
        output_options=output_options,
        block=block,
        table=table,
        specout=specout,
    )
    rendered = output.render()
    print("")
    print(rendered)
    # Verify nest is rendered
    assert "NGRID sname='child1'" in rendered
    assert "NESTOUT sname='child1'" in rendered


def test_output_sname_unique(frame, group):
    group1 = copy.deepcopy(group)
    group1.sname = frame.sname
    with pytest.raises(ValidationError):
        OUTPUT(frame=frame, group=group1)


def test_output_block_frame_or_group(points):
    block = BLOCK(sname="outpts", fname="./depth-frame.nc", output=["depth"])
    with pytest.raises(ValidationError):
        OUTPUT(points=points, block=block)


def test_output_block_frame_or_group(points):
    block = BLOCK(sname="outpts", fname="./depth-frame.nc", output=["depth"])
    with pytest.raises(ValidationError):
        OUTPUT(points=points, block=block)


def test_output_write_locations_exist(table):
    with pytest.raises(ValidationError):
        OUTPUT(table=table)


def test_output_ray_defined_if_isoline(isoline):
    with pytest.raises(ValidationError):
        OUTPUT(isoline=isoline)


def test_output_ray_rname_matches_isoline_rname(isoline, ray):
    isoline.rname = "dummy"
    with pytest.raises(ValidationError):
        OUTPUT(isoline=isoline, ray=ray)


def test_output_ngrid_nestout_defined(ngrid, nestout):
    with pytest.raises(ValidationError):
        OUTPUT(ngrid=ngrid)
        OUTPUT(nestout=nestout)


def test_output_sname_ngrid_nestout_match(ngrid, nestout):
    ngrid.sname = "dummy"
    with pytest.raises(ValidationError):
        OUTPUT(ngrid=ngrid, nestout=nestout)


# =====================================================================================
# Additional NEST Component Tests
# =====================================================================================

def test_nest(nest):
    """Test basic NEST component rendering."""
    assert "NGRID sname='child1'" in nest.render()
    assert "NESTOUT sname='child1'" in nest.render()


def test_nest_sname_sync():
    """Test that sname is automatically synced to child components."""
    nest = NEST(
        sname="test",
        ngrid=NGRID(
            sname="other",
            grid=dict(xp=167.0, yp=-45.5, xlen=0.1, ylen=0.1, mx=12, my=14),
        ),
        nestout=NESTOUT(
            sname="another",
            fname="nestout.swn",
            times=dict(tfmt=1, dfmt="hr"),
        ),
    )
    assert nest.ngrid.sname == "test"
    assert nest.nestout.sname == "test"


def test_output_multiple_nests(times):
    """Test OUTPUT component with multiple nests."""
    output = OUTPUT(
        nests=[
            dict(
                sname="child_1",
                ngrid=dict(
                    model_type="ngrid",
                    grid=dict(xp=167.0, yp=-45.5, xlen=0.1, ylen=0.1, mx=12, my=14),
                ),
                nestout=dict(fname="nestout_child1.swn", times=times),
            ),
            dict(
                sname="child_2",
                ngrid=dict(
                    model_type="ngrid",
                    grid=dict(xp=166.0, yp=-46.5, xlen=0.1, ylen=0.1, mx=8, my=6),
                ),
                nestout=dict(fname="nestout_child2.swn", times=times),
            ),
        ],
    )
    assert len(output.nests) == 2
    rendered = output.render()
    assert "NGRID sname='child_1'" in rendered
    assert "NGRID sname='child_2'" in rendered


def test_output_nests_unique_snames(times):
    """Test that duplicate nest snames are rejected."""
    with pytest.raises(ValidationError, match="Duplicate nest snames"):
        OUTPUT(
            nests=[
                dict(
                    sname="child",
                    ngrid=dict(
                        model_type="ngrid",
                        grid=dict(xp=167.0, yp=-45.5, xlen=0.1, ylen=0.1, mx=12, my=14),
                    ),
                    nestout=dict(fname="nestout1.swn", times=times),
                ),
                dict(
                    sname="child",
                    ngrid=dict(
                        model_type="ngrid",
                        grid=dict(xp=166.0, yp=-46.5, xlen=0.1, ylen=0.1, mx=8, my=6),
                    ),
                    nestout=dict(fname="nestout2.swn", times=times),
                ),
            ],
        )
