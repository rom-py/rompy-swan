"""Base class for SWAN components.

How to subclass
---------------

- Define a new `model_type` Literal for the subclass (set the default value to avoid
  having to set it when instantiating the object)
- Overwrite the __repr__ method to return the SWAN input file string

"""
import logging
from typing_extensions import Literal

from rompy.core import RompyBaseModel


logger = logging.getLogger(__name__)

MAX_LENGTH = 132


def split_string(cmd: str, max_length: int = MAX_LENGTH, spaces: int = 4) -> list:
    """Split command cmd if longer than max_length.

    Parameters
    ----------
    cmd: str
        SWAN CMD string to split.
    max_length: int
        Maximum length of each split string.
    spaces: int
        Number of spaces in each identation before each new line.

    Returns
    -------
    list
        Split string.

    """
    if len(cmd) <= max_length:
        return [cmd]

    split_index = cmd.rfind(" ", 0, max_length - 1 - spaces)

    if split_index == -1:
        split_index = max_length

    return [cmd[:split_index]] + split_string(cmd[split_index+1:])


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

    def render(self) -> str:
        """Render the component to a CMD string."""
        spaces = 4
        # Split cmd at existing newlines
        cmd_lines = self.__repr__().split("\n")
        # Split each line before max_length
        cmds = []
        for cmd in cmd_lines:
            cmds.extend(split_string(cmd, max_length=MAX_LENGTH, spaces=spaces))
        # Return joined string with newline representations
        return f" &\n{spaces * ' '}".join(cmds)
