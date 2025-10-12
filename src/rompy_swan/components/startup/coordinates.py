"""SWAN COORDINATES component."""

from typing import Literal

from pydantic import Field

from rompy_swan.components.base import BaseComponent
from rompy_swan.components.startup.options.coords import CARTESIAN, SPHERICAL


class COORDINATES(BaseComponent):
    """SWAN Coordinates.

    .. code-block:: text

        COORDINATES ->CARTESIAN|SPHERICAL REPEATING

    Command to choose between Cartesian and spherical coordinates (see Section 2.5).
    A nested SWAN run must use the same coordinate system as the coarse grid SWAN run.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.startup.coordinates import COORDINATES
        coords = COORDINATES()
        print(coords.render())
        coords = COORDINATES(
            kind=dict(model_type="spherical", projection="ccm"),
            reapeating=True,
        )
        print(coords.render())

    """

    model_type: Literal["coordinates", "COORDINATES"] = Field(
        default="coordinates",
        description="Model type discriminator",
    )
    kind: CARTESIAN | SPHERICAL = Field(
        default_factory=CARTESIAN,
        description="Coordinates kind",
    )
    reapeating: bool = Field(
        default=False,
        description=(
            "This option is only for academic cases. It means that wave energy "
            "leaving at one end of the domain (in computational x-direction) enter at "
            "the other side; it is as if the wave field repeats itself in x-direction "
            "with the length of the domain in x-direction. This option cannot be used "
            "in combination with computation of set-up (see command SETUP). This "
            "option is available only with regular grids"
        ),
    )

    def cmd(self) -> str:
        repr = f"COORDINATES {self.kind.render()}"
        if self.reapeating:
            repr += " REPEATING"
        return repr
