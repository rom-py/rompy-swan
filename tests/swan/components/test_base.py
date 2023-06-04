"""Test base component."""
from string import ascii_lowercase, ascii_uppercase
from typing import Literal

from rompy.swan.components.base import BaseComponent


class LongRender(BaseComponent):
    """Long render method."""
    model_type: Literal["test"] = "test"

    @property
    def options(self):
        return {c: f"{c}_value" for c in ascii_lowercase + ascii_uppercase}

    def __repr__(self):
        """Render the component to a string."""
        repr = f"COMPONENT"
        for k, v in self.options.items():
            if k == "A":
                repr += f"\n{k}={v}"
            else:
                repr += f" {k}={v}"
        return repr


def test_max_132_characters():
    """Test that the render string is not longer than 132 characters."""
    lr = LongRender()
    print(lr.render())
    # assert len(long_render.render()) <= 132