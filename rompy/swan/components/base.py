"""Base class for SWAN components."""
from enum import Enum
from rompy.core import RompyBaseModel


class BaseComponent(RompyBaseModel):
    """Base class for SWAN components."""

    def render(self):
        """Render the component to a string."""
        return self.__repr__()


class FormatEnum(str, Enum):
    """Enum for SWAN format types."""
    free = "free"
    fixed = "fixed"
    unformatted = "unformatted"
