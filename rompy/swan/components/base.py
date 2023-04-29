"""Base class for SWAN components."""
from enum import Enum
from rompy.core import RompyBaseModel


class BaseComponent(RompyBaseModel):
    """Base class for SWAN components.

    Parameters
    ----------
    name : str
        Name of the component which is render as a comment in the cmd file.

    """

    name: str

    @property
    def header(self):
        return f"\n!{self.name.center(131, '-')}\n"

    def render(self):
        """Render the component to a string."""
        return f"{self.header}{self.__repr__()}\n"


class FormatEnum(str, Enum):
    """Enum for SWAN format types."""
    free = "free"
    fixed = "fixed"
    unformatted = "unformatted"
