"""Test inpgrid component."""
import pytest
from pydantic import ValidationError

from rompy.swan.components.inpgrid import (
    INPGRID,
    REGULAR,
    CURVILINEAR,
    UNSTRUCTURED,
    InpgridOptions,
)


def test_valid_inpgrid_optins():
    for inpgrid in InpgridOptions:
        INPGRID(inpgrid=inpgrid.value)
        INPGRID(inpgrid=inpgrid.value.lower())
        INPGRID(inpgrid=inpgrid.value.upper())
    with pytest.raises(ValidationError):
        INPGRID(inpgrid="invalid")
