"""Base class for SWAN components.

How to subclass
---------------

- Define a new `kind` Literal type for the subclass
- Overwrite the __repr__ method to return the SWAN input file string

"""
from enum import Enum
from typing_extensions import Literal
from pydantic import BaseModel, root_validator

from rompy.core import RompyBaseModel

# class BaseComponent(RompyBaseModel):
class BaseComponent(BaseModel):
    """Base class for SWAN components.

    Parameters
    ----------
    kind : Literal["base"]
        Name of the component to help parsing and render as a comment in the cmd file.

    Behaviour
    ---------
    - Make all string input case-insensitive.
    - Define a header from parent classes names and the component kind.
    - Define a render method to render the component to a cmd string.

    """

    kind: Literal["base"]

    @root_validator(pre=True)
    def to_lowercase(cls, values):
        """Make all string input case-insensitive."""
        values = {k: v.lower() if isinstance(v, str) else v for k, v in values.items()}
        return values

    @property
    def header(self):
        """Define a header from parent classes names and the component kind."""
        s = " ".join([c.__name__ for c in self.__class__.__bases__] + [self.kind.upper()])
        return f"\n!{s.center(131, '-')}\n"

    def render(self):
        """Render the component to a string."""
        return f"{self.header}{self.__repr__()}\n"
