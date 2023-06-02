"""Base class for SWAN components.

How to subclass
---------------

- Define a new `type` Literal type for the subclass
- Overwrite the __repr__ method to return the SWAN input file string

"""
import logging
from typing_extensions import Literal

from rompy.core import RompyBaseModel


logger = logging.getLogger(__name__)


class BaseComponent(RompyBaseModel):
    """Base class for SWAN components.

    Parameters
    ----------
    model_type: Literal["component"]
        Model type discriminator.

    Behaviour
    ---------
    - Define a render method to render the component to a cmd string.
    - Restrict arguments to the defined ones.

    """

    model_type: Literal["component"]

    class Config:
        """Configure the model."""
        extra = "forbid"

    def render(self):
        """Render the component to a string."""
        return f"{self.__repr__()}"
