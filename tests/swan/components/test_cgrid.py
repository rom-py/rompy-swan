"""Test cgrid component."""
import pytest

from rompy.swan.components.cgrid import (
    CGrid,
    CGridRegular,
    CGridCurvilinear,
    CGridUnstructured,
    ReadGridCoord,
)


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


def test_curvilinear_grid():
    cgrid = CGridCurvilinear(mdc=36, flow=0.04, fhigh=0.4, mxc=10, myc=10)


def test_curvilinear_grid_exception():
    cgrid = CGridCurvilinear(
        mdc=36, flow=0.04, fhigh=0.4, mxc=10, myc=10, xexc=-999.0, yexc=-999.0
    )
    with pytest.raises(ValueError):
        cgrid = CGridCurvilinear(
            mdc=36, flow=0.04, fhigh=0.4, mxc=10, myc=10, xexc=-999.0
        )
    with pytest.raises(ValueError):
        cgrid = CGridCurvilinear(
            mdc=36, flow=0.04, fhigh=0.4, mxc=10, myc=10, yexc=-999.0
        )


def test_unstructured_grid():
    cgrid = CGridUnstructured(mdc=36, flow=0.04, fhigh=0.4)


def test_read_grid_coord_free_or_fixed_or_unformatted_only():
    rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed", form="(10X,12F5.0)")
    rgc = ReadGridCoord(fname="grid_coord.txt", format="free")
    rgc = ReadGridCoord(fname="grid_coord.txt", format="unformatted")
    with pytest.raises(ValueError):
        rgc = ReadGridCoord(fname="grid_coord.txt", format="something_else")


def test_read_grid_coord_idfm_options():
    rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed", idfm=1)
    rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed", idfm=5)
    rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed", idfm=6)
    rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed", idfm=8)
    with pytest.raises(ValueError):
        rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed", idfm=9)


def test_fixed_format_arguments():
    rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed", form="(10X,12F5.0)")
    rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed", idfm=1)
    with pytest.raises(ValueError):
        rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed", idfm=5, form="(10X,12F5.0)")
    with pytest.raises(ValueError):
        rgc = ReadGridCoord(fname="grid_coord.txt", format="fixed")