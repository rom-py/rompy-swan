"""Test output components."""
import pytest
from pydantic import ValidationError

from rompy.swan.components.output import (
    BaseLocation,
    FRAME,
    TABLE,
)


def test_base_location():
    loc = BaseLocation(sname="outsites")
    assert loc.render() == "LOCATIONS sname='outsites'"


def test_sname_lt8():
    with pytest.raises(ValidationError):
        BaseLocation(sname="outputlocations")


def test_sname_not_special():
    with pytest.raises(ValidationError):
        BaseLocation(sname="BOTTGRID")
        BaseLocation(sname="COMPGRID")


# def test_table():
#     table = TABLE(
#         sname="outpoints",
#         format="noheader",
#         fname="./output_table.nc",
#         output=["hsign", "hswell", "dir", "tps", "tm01", "watlev", "qp"],
#         # time=dict(tbeg="2012-01-01T00:00:00", delt="PT30M", deltfmt="min"),
#     )
#     print(table.render())