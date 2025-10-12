"""SWAN physics deactivation components.

This module contains components for deactivating physics processes in SWAN.
"""

from typing import Literal

from pydantic import Field

from rompy_swan.components.base import BaseComponent
from rompy_swan.types import PhysicsOff


class OFF(BaseComponent):
    """Deactivate physics commands.

    .. code-block:: text

        OFF WINDGROWTH|QUADRUPL|WCAPPING|BREAKING|REFRAC|FSHIFT|BNDCHK

    This command deactivates physics commands. The command can be used to switch off
    the computation of a certain physics component without having to remove the command
    from the input file. This is useful for testing purposes.

    Examples
    --------

    .. ipython:: python

        from rompy_swan.components.physics import OFF
        off = OFF(physics="windgrowth")
        print(off.render())

    """

    model_type: Literal["off", "OFF"] = Field(
        default="off", description="Model type discriminator"
    )
    physics: PhysicsOff = Field(description="Physics command to be switched off")

    def cmd(self) -> str:
        """Command file string for this component."""
        return f"OFF {self.physics.value.upper()}"


class OFFS(BaseComponent):
    """Deactivate multiple physics commands.

    .. code-block:: text

        OFF WINDGROWTH|QUADRUPL|WCAPPING|BREAKING|REFRAC|FSHIFT|BNDCHK
        OFF WINDGROWTH|QUADRUPL|WCAPPING|BREAKING|REFRAC|FSHIFT|BNDCHK
        .

    This group component is a convenience to allow defining and rendering
    a list of `OFF` components.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import OFFS
        off1 = dict(physics="windgrowth")
        off2 = dict(physics="wcapping")
        offs = OFFS(offs=[off1, off2])
        for off in offs.render():
            print(off)

    """

    model_type: Literal["offs", "OFFS"] = Field(
        default="offs", description="Model type discriminator"
    )
    offs: list[OFF] = Field(description="Physics commands to deactivate")

    def cmd(self) -> list:
        """Command file strings for this component."""
        repr = []
        for off in self.offs:
            repr += [off.cmd()]
        return repr

    def render(self) -> str:
        """Override base class to allow rendering list of components."""
        cmds = []
        for cmd in self.cmd():
            cmds.append(super().render(cmd))
        return cmds
