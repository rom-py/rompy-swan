"""Test cgrid component."""
import pytest

from rompy.swan.components.cgrid import (
    CGrid,
    CGridRegular,
    CGridCurvilinear,
    CGridUnstructured,
)



@pytest.fixture(scope="module")
def curvilinear_kwargs():
    yield dict(mdc=36, flow=0.04, fhigh=0.4, mxc=10, myc=10, fname="grid_coord.txt")


def test_msc_gt_3():
    with pytest.raises(ValueError):
        cgrid = CGrid(mdc=36, msc=2)


def test_circle():
    cgrid = CGrid(mdc=36, flow=0.04, fhigh=0.4)
    assert cgrid.dir_sector == "CIRCLE"


def test_sector():
    cgrid = CGrid(mdc=36, flow=0.04, fhigh=0.4, dir1=0.0, dir2=180.0)
    assert cgrid.dir_sector == "SECTOR 0.0 180.0"


def test_dir1_and_dir2():
    with pytest.raises(ValueError):
        cgrid = CGrid(mdc=36, flow=0.04, fhigh=0.4, dir1=45.0)


def test_freq_args_at_least_two():
    with pytest.raises(ValueError):
        cgrid = CGrid(mdc=36, flow=0.04)


def test_flow_less_than_fhigh():
    with pytest.raises(ValueError):
        cgrid = CGrid(mdc=36, flow=0.4, fhigh=0.04)


def test_cgrid():
    cgrid = CGrid(mdc=36, flow=0.04, fhigh=0.4, msc=28, dir1=None, dir2=None)


def test_regular_grid():
    cgrid = CGridRegular(
        mdc=36,
        flow=0.04,
        fhigh=0.4,
        xpc=0.0,
        ypc=0.0,
        alpc=0.0,
        xlenc=100.0,
        ylenc=100.0,
        mxc=10,
        myc=10,
    )


def test_curvilinear_grid(curvilinear_kwargs):
    CGridCurvilinear(**curvilinear_kwargs)


def test_curvilinear_grid_exception(curvilinear_kwargs):
    CGridCurvilinear(xexc=-999.0, yexc=-999.0, **curvilinear_kwargs)
    with pytest.raises(ValueError):
        CGridCurvilinear(xexc=-999.0, **curvilinear_kwargs)
    with pytest.raises(ValueError):
        CGridCurvilinear(yexc=-999.0, **curvilinear_kwargs)


def test_read_grid_coord_free_or_fixed_or_unformatted_only(curvilinear_kwargs):
    CGridCurvilinear(format="fixed", form="(10X,12F5.0)", **curvilinear_kwargs)
    CGridCurvilinear(format="free", **curvilinear_kwargs)
    CGridCurvilinear(format="unformatted", **curvilinear_kwargs)
    with pytest.raises(ValueError):
        CGridCurvilinear(format="something_else", **curvilinear_kwargs)


def test_read_grid_coord_idfm_options(curvilinear_kwargs):
    CGridCurvilinear(format="fixed", idfm=1, **curvilinear_kwargs)
    CGridCurvilinear(format="fixed", idfm=5, **curvilinear_kwargs)
    CGridCurvilinear(format="fixed", idfm=6, **curvilinear_kwargs)
    CGridCurvilinear(format="fixed", idfm=8, **curvilinear_kwargs)
    with pytest.raises(ValueError):
        CGridCurvilinear(format="fixed", idfm=9, **curvilinear_kwargs)


def test_fixed_format_arguments(curvilinear_kwargs):
    CGridCurvilinear(format="fixed", form="(10X,12F5.0)", **curvilinear_kwargs)
    CGridCurvilinear(format="fixed", idfm=1, **curvilinear_kwargs)
    with pytest.raises(ValueError):
        CGridCurvilinear(format="fixed", idfm=5, form="(10X,12F5.0)", **curvilinear_kwargs)
    with pytest.raises(ValueError):
        CGridCurvilinear(format="fixed", **curvilinear_kwargs)


def test_unstructured_grid():
    cgrid = CGridUnstructured(mdc=36, flow=0.04, fhigh=0.4)
