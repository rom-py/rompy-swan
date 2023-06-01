"""Base class for SWAN sub-components."""
from typing import Literal
from abc import ABC
from rompy.core import RompyBaseModel


class BaseSubComponent(RompyBaseModel, ABC):
    """Base class for SWAN sub-components.

    Parameters
    ----------
    model_type: Literal["subcomponent"]
        Model type discriminator.

    Behaviour
    ---------
    - Define a render method to render the component to a cmd string.
    - Restrict arguments to the defined ones.

    """

    model_type: Literal["subcomponent"]

    class Config:
        """Configure the model."""
        extra = "forbid"

    def render(self):
        """Render the sub-component to a string."""
        return f"{self.__repr__()}"
