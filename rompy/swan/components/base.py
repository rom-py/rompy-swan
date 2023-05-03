"""Base class for SWAN components.

How to subclass
---------------

- Define a new `kind` Literal type for the subclass
- Overwrite the __repr__ method to return the SWAN input file string

"""
from enum import Enum
from typing_extensions import Literal
from pydantic import BaseModel

from rompy.core import RompyBaseModel

# class BaseComponent(RompyBaseModel):
class BaseComponent(BaseModel):
    """Base class for SWAN components.

    Parameters
    ----------
    kind : Literal["base"]
        Name of the component to help parsing and render as a comment in the cmd file.

    """

    kind: Literal["base"]

    @property
    def header(self):
        s = " ".join([c.__name__ for c in self.__class__.__bases__] + [self.kind])
        return f"\n!{s.center(131, '-')}\n"

    def render(self):
        """Render the component to a string."""
        return f"{self.header}{self.__repr__()}\n"


class FormatEnum(str, Enum):
    """Enum for SWAN format types."""
    free = "free"
    fixed = "fixed"
    unformatted = "unformatted"
