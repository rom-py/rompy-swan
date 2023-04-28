"""Base class for SWAN components."""
from rompy.core import RompyBaseModel


class BaseComponent(RompyBaseModel):
    """Base class for SWAN components."""

    def render(self):
        """Render the component to a string."""
        return self.__repr__()
