"""Test output components."""
import pytest
from pydantic import ValidationError

from rompy.swan.components.output import (
    TABLE,
)


def test_table():
    table = TABLE(
        sname="outpoints",
        format="noheader",
        fname="./output_table.nc",
        output=["hsign", "hswell", "dir", "tps", "tm01", "watlev", "qp"],
        # time=dict(tbeg="2012-01-01T00:00:00", delt="PT30M", deltfmt="min"),
    )
    print(table.render())