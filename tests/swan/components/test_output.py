"""Test output components."""
import pytest
import re
from pydantic import ValidationError

from rompy.swan.components.output import (
    SPECIAL_NAMES,
    BaseLocation,
    FRAME,
    GROUP,
    CURVE,
    CURVES,
    RAY,
    ISOLINE,
    POINTS,
    POINTS_FILE,
    NGRID,
    NGRID_UNSTRUCTURED,
    TABLE,
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


def test_frame():
    loc = FRAME(
        sname="outgrid",
        grid=dict(xp=173, yp=-40, xlen=2, ylen=2, mx=19, my=19),
    )
    assert loc.render() == (
        "FRAME sname='outgrid' xpfr=173.0 ypfr=-40.0 alpfr=0.0 "
        "xlenfr=2.0 ylenfr=2.0 mxfr=19 myfr=19"
    )


def test_group():
    loc = GROUP(sname="subgrid", ix1=20, iy1=0, ix2=50, iy2=100)
    loc.render() == "GROUP sname='subgrid' SUBGRID ix1=20 iy1=0 ix2=50 iy2=100"


def test_curve():
    loc = CURVE(
        sname="outcurve",
        xp1=172,
        yp1=-40,
        npts=[3, 3],
        xp=[172.0, 174.0],
        yp=[-38.0, -38.0],
    )
    assert "CURVE sname='outcurve'" in loc.render()


def test_curve():
    curve1 = CURVE(
        sname="curve1",
        xp1=172,
        yp1=-40,
        npts=[3, 3],
        xp=[172.0, 174.0],
        yp=[-38.0, -38.0],
    )
    curve2 = CURVE(
        sname="curve2",
        xp1=172.5,
        yp1=-39.2,
        npts=[5, 5],
        xp=[173.5, 174.5],
        yp=[-32.1, -39.0],
    )
    loc = CURVES(curves=[curve1, curve2])
    assert loc.render().count("CURVE sname=") == 2


def test_ray():
    loc = RAY(
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
    assert loc.render().startswith("CURVE rname='outray'")


def test_isoline():
    loc = ISOLINE(sname="outcurve", rname="outray", dep_type="depth", dep=12.0)
    assert loc.render() == "ISOLINE sname='outcurve' rname='outray' DEPTH dep=12.0"


def test_points():
    loc = POINTS(sname="outpts", xp=[172.3, 172.4], yp=[-39, -39])
    assert loc.render().startswith("POINTS sname='outpts' &")


def test_points_file():
    loc = POINTS_FILE(sname="outpts", fname="./output_points.nc")
    assert loc.render() == "POINTS sname='outpts' fname='./output_points.nc'"


def test_ngrid():
    loc = NGRID(
        sname="outnest", grid=dict(xp=173, yp=-40, xlen=2, ylen=2, mx=19, my=19),
    )
    assert loc.render() == (
        "NGRID xpn=173.0 ypn=-40.0 alpn=0.0 xlenn=2.0 ylenn=2.0 mxn=19 myn=19"
    )


def test_ngrid_unstructured():
    loc = NGRID_UNSTRUCTURED(sname="outnest", kind="triangle", fname="./ngrid.txt")
    assert loc.render() == (
        "NGRID sname='outnest' UNSTRUCTURED TRIANGLE fname='./ngrid.txt'"
    )


    # print(loc.render())


# def test_table():
#     table = TABLE(
#         sname="outpoints",
#         format="noheader",
#         fname="./output_table.nc",
#         output=["hsign", "hswell", "dir", "tps", "tm01", "watlev", "qp"],
#         # time=dict(tbeg="2012-01-01T00:00:00", delt="PT30M", deltfmt="min"),
#     )
#     print(table.render())