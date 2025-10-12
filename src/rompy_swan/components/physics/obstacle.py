"""SWAN obstacle components.

This module contains components for configuring obstacles in SWAN.
"""

from typing import Annotated, Literal, Optional, Union

from pydantic import Field, model_validator

from rompy.logging import get_logger
from rompy_swan.components.base import BaseComponent
from rompy_swan.components.physics._reflection import (
    FREEBOARD,
    LINE,
    RDIFF,
    REFL,
    RSPEC,
)
from rompy_swan.components.physics._transmission import (
    DANGREMOND,
    GODA,
    TRANS1D,
    TRANS2D,
    TRANSM,
)

logger = get_logger(__name__)


TRANSMISSION_TYPE = Annotated[
    Union[TRANSM, TRANS1D, TRANS2D, GODA, DANGREMOND],
    Field(description="Wave transmission", discriminator="model_type"),
]
REFLECTION_TYPE = Annotated[
    Union[RSPEC, RDIFF],
    Field(description="Wave reflection type", discriminator="model_type"),
]


class OBSTACLE(BaseComponent):
    """Subgrid obstacle.

    .. code-block:: text

        OBSTACLE ->TRANSM|TRANS1D|TRANS2D|GODA|DANGREMOND REFL [reflc] ->RSPEC|RDIFF &
            (FREEBOARD [hgt] [gammat] [gammar] QUAY) LINE < [xp] [yp] >

    With this optional command the user provides the characteristics of a (line
    of) sub-grid obstacle(s) through which waves are transmitted or against which
    waves are reflected (possibly both at the same time). The obstacle is sub-grid
    in the sense that it is narrow compared to the spatial meshes; its length should
    be at least one mesh length.

    The location of the obstacle is defined by a sequence of corner points of a line.
    The obstacles interrupt the propagation of the waves from one grid point to the
    next wherever this obstacle line is located between two neighbouring grid points
    (of the computational grid; the resolution of the obstacle is therefore equal to
    the computational grid spacing). This implies that an obstacle to be effective must
    be located such that it crosses at least one grid line. This is always the case
    when an obstacle is larger than one mesh length.

    Notes
    -----

    * The advise is to define obstacles with the least amount of points possible.
    * SWAN checks if the criterion `reflc^2 + trcoef^2 LE 1` is fulfilled.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import OBSTACLE
        obs = OBSTACLE(
            transmission=dict(model_type="transm", trcoef=0.5),
            reflection=dict(reflc=0.5),
            line=dict(xp=[174.1, 174.2, 174.3], yp=[-39.1, -39.1, -39.1]),
        )
        print(obs.render())

    """

    model_type: Literal["obstacle", "OBSTACLE"] = Field(
        default="obstacle", description="Model type discriminator"
    )
    transmission: Optional[TRANSMISSION_TYPE] = Field(default=None)
    reflection: Optional[REFL] = Field(default=None, description="Wave reflection")
    reflection_type: Optional[REFLECTION_TYPE] = Field(default=None)
    freeboard: Optional[FREEBOARD] = Field(default=None, description="Freeboard")
    line: LINE = Field(default=None, description="Line of obstacle")

    @model_validator(mode="after")
    def hgt_consistent(self) -> "OBSTACLE":
        """Warns if `hgt` has different values in DAM and FREEBOARD specifications."""
        if self.transmission is not None and self.freeboard is not None:
            is_dam = self.transmission.model_type.upper() in ["GODA", "DANGREMOND"]
            if is_dam and self.freeboard.hgt != self.transmission.hgt:
                logger.warning("hgt in FREEBOARD and DAM specifications are not equal")
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "OBSTACLE"
        if self.transmission is not None:
            repr += f" {self.transmission.render()}"
        if self.reflection:
            repr += f" {self.reflection.render()}"
        if self.reflection_type is not None:
            repr += f" {self.reflection_type.render()}"
        if self.freeboard is not None:
            repr += f" {self.freeboard.render()}"
        repr += f" {self.line.render()}"
        return repr


class OBSTACLE_FIG(BaseComponent):
    """Obstacle for free infragravity radiation.

    .. code-block:: text

        OBSTACLE FIG [alpha1] [hss] [tss] (REFL [reflc]) LINE <[xp] [yp]>

    With this optional command the user specifies the obstacles along which the
    free infra-gravity (FIG) energy is radiated. By placing the obstacles close to
    the shorelines SWAN will include the FIG source term along the coastlines
    according to the parametrization of Ardhuin et al. (2014).

    The location of the obstacle is defined by a sequence of corner points of a line.
    For an obstacle line to be effective its length is at least one mesh size large. It
    is recommended to place the obstacles at the inner area of the computational grid,
    not at or through the boundaries. In particular, each obstacle line must be
    bordered by wet points on both sides.

    In addition, the orientation of the obstacle line determines from which side of the
    obstacle the FIG wave energy is radiated away. If the begin point of the line is
    below or left of the end point, that is, pointing upwards/to the right, then FIG
    energy is radiated from the west/north side of the line. If the begin point is
    above or right of the end point (pointing downwards/to the left), then FIG energy
    is radiated away from the east/south side of the obstacle line.

    References
    ----------
    Ardhuin, F., Rawat, A. and Aucan, J., 2014. A numerical model for free
    infragravity waves: Definition and validation at regional and global scales.
    Ocean Modelling, 77, pp.20-32.

    Notes
    -----
    Either `hss` or `tss` or both are allowed to vary over the computational domain.
    In that case use the commands `INPGRID HSS` and `READINP HSS` and/or the commands
    `INPGRID TSS` and `READINP TSS` to define and read the sea-swell wave height/period
    It is permissible to have constant sea-swell height and non-constant sea-swell
    period, or vice versa. The command `OBST FIG` is still required to define the
    obstacles. The values of `hss` and/or `tss` in this command are then not required
    (they will be ignored).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import OBSTACLE_FIG
        obs = OBSTACLE_FIG(
            alpha1=5e-4,
            hss=2.5,
            tss=10.3,
            line=dict(xp=[174.1, 174.2, 174.3], yp=[-39.1, -39.1, -39.1]),
        )
        print(obs.render())
        obs = OBSTACLE_FIG(
            alpha1=5e-4,
            hss=2.5,
            tss=10.3,
            reflection=dict(reflc=0.5),
            line=dict(xp=[174.1, 174.2, 174.3], yp=[-39.1, -39.1, -39.1]),
        )
        print(obs.render())

    """

    model_type: Literal["fig", "FIG"] = Field(
        default="fig", description="Model type discriminator"
    )
    alpha1: float = Field(
        description=(
            "Calibration parameter (in 1/s) for determining the rate of radiating FIG "
            "energy from the shorelines, values in Table 1 of Ardhuin et al. (2014) "
            "are between 4e-4 and 8.1e-4"
        ),
    )
    hss: float = Field(
        description="The sea-swell significant wave height (in m)",
        ge=0.0,
    )
    tss: float = Field(
        description="The sea-swell mean wave period (in s)",
        ge=0.0,
    )
    reflection: Optional[REFL] = Field(default=None, description="Wave reflection")
    line: LINE = Field(description="Line of obstacle")

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"OBSTACLE FIG alpha1={self.alpha1} hss={self.hss} tss={self.tss}"
        if self.reflection:
            repr += f" {self.reflection.render()}"
        repr += f" {self.line.render()}"
        return repr


OBSTACLES_TYPE = Annotated[
    Union[OBSTACLE, OBSTACLE_FIG],
    Field(discriminator="model_type"),
]


class OBSTACLES(BaseComponent):
    """List of swan obstacles.

    .. code-block:: text

        OBSTACLE ... LINE < [xp] [yp] >
        OBSTACLE ... LINE < [xp] [yp] >
        .

    This group component is a convenience to allow defining and rendering
    a list of obstacle components.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.physics import OBSTACLES, OBSTACLE, OBSTACLE_FIG
        obst1 = dict(
            model_type="obstacle",
            reflection=dict(reflc=1.0),
            line=dict(xp=[174.1, 174.2, 174.3], yp=[-39.1, -39.1, -39.1]),
        )
        obst2 = OBSTACLE(
            transmission=dict(model_type="transm"),
            line=dict(xp=[174.3, 174.3], yp=[-39.1, -39.2]),
        )
        obst3 = OBSTACLE_FIG(
            alpha1=5e-4,
            hss=2.5,
            tss=10.3,
            line=dict(xp=[174.1, 174.2, 174.3], yp=[-39.1, -39.1, -39.1]),
        )
        obstacles = OBSTACLES(obstacles=[obst1, obst2, obst3])
        for obst in obstacles.render():
            print(obst)

    """

    model_type: Literal["obstacles", "OBSTACLES"] = Field(
        default="obstacles", description="Model type discriminator"
    )
    obstacles: list[OBSTACLES_TYPE] = Field(description="List of obstacles")

    def cmd(self) -> list:
        """Command file strings for this component."""
        repr = []
        for obstacle in self.obstacles:
            repr += [obstacle.cmd()]
        return repr

    def render(self) -> str:
        """Override base class to allow rendering list of components."""
        cmds = []
        for cmd in self.cmd():
            cmds.append(super().render(cmd))
        return cmds
