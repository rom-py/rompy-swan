"""Base class for SWAN sub-components."""
from typing import Literal
from abc import ABC
from pydantic import ConfigDict, Field

from rompy.core import RompyBaseModel


class BaseSubComponent(RompyBaseModel, ABC):
    """Base class for SWAN sub-components.

    Behaviour
    ---------
    - Define a render method to render the component to a cmd string.
    - Restrict arguments to the defined ones.

    """

    model_type: Literal["subcomponent"] = Field(description="Model type discriminator")
    model_config = ConfigDict(extra="forbid")

    def cmd(self) -> str:
        return self.model_type.upper()

    def render(self) -> str:
        """Render the sub-component to a string."""
        return self.cmd()
