"""SWAN mud component.

This module contains the MUD component for wave damping due to mud in SWAN.
"""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class MUD(BaseComponent):
    """Mud dumping.

    .. code-block:: text

        MUD [layer] [rhom] [viscm]

    With this command the user can activate wave damping due to mud based on Ng (2000).
    If this command or the commands INPGRID MUDLAY and READINP MUDLAY are not used,
    SWAN will not account for muddy bottom effects.

    References
    ----------
    Ng, C., 2000, Water waves over a muddy bed: A two layer Stokes' boundary layer
    model, Coastal Eng., 40, 221-242.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import MUD
        mud = MUD()
        print(mud.render())
        mud = MUD(
            layer=2.0,
            rhom=1300,
            viscm=0.0076,
        )
        print(mud.render())

    TODO: Validate `layer` must be prescribed if `INPGRID MUDLAY` isn't used.

    """

    model_type: Literal["mud", "MUD"] = Field(
        default="mud", description="Model type discriminator"
    )
    layer: Optional[float] = Field(
        default=None,
        description=(
            "The thickness of the mud layer (in m). Note that `layer` is allowed to "
            "vary over the computational region to account for the zonation of muddy "
            "bottom. In that case use the commands `INPGRID MUDLAY` and `READINP "
            "MUDLAY` to define and read the layer thickness of mud. The value of "
            "`layer` in this command is then not required (it will be ignored)"
        ),
    )
    rhom: Optional[float] = Field(
        default=None,
        description="The density of the mud layer (in kg/m3) (SWAN default: 1300)",
    )
    viscm: Optional[float] = Field(
        default=None,
        description=(
            "The kinematic viscosity of the mud layer (in m2/s) (SWAN default: 0.0076)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "MUD"
        if self.layer is not None:
            repr += f" layer={self.layer}"
        if self.rhom is not None:
            repr += f" rhom={self.rhom}"
        if self.viscm is not None:
            repr += f" viscm={self.viscm}"
        return repr
