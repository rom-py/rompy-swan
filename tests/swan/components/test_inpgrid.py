"""Test inpgrid component."""
import pytest
from pydantic import ValidationError

from rompy.swan.components.inpgrid import (
    INPGRID,
)


def test_inpgrid_definition_lower_upper_short_long():
    """Test valid ways to define the input grid type.

    Valid options are:
    - Full word with the upper and lower case componts as defined in the manual.
    - Full word either all in upper case or all in lower case.
    - Sub-word defined by the upper case characters (lower case accepted).

    """
    INPGRID(inpgrid="BOTtom")
    INPGRID(inpgrid="BOTTOM")
    INPGRID(inpgrid="bottom")
    INPGRID(inpgrid="BOT")
    INPGRID(inpgrid="bot")
    with pytest.raises(ValidationError):
        INPGRID(inpgrid="bOTOOM")
