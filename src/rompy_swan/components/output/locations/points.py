"""SWAN output component."""

from typing import Literal, Optional

from pydantic import Field, model_validator


from rompy_swan.components.output.locations import BaseLocation


class POINTS(BaseLocation):
    """Isolated output locations.

    .. code-block:: text

        POINTS 'sname' < [xp] [yp] >

    With this optional command the user defines a set of individual output point
    locations.

    Note
    ----
    All coordinates and distances should be given in m when Cartesian coordinates are
    used or degrees when Spherical coordinates are used (see command COORD).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import POINTS
        loc = POINTS(sname="outpts", xp=[172.3, 172.4], yp=[-39, -39])
        print(loc.render())

    """

    model_type: Literal["points", "POINTS"] = Field(
        default="points", description="Model type discriminator"
    )
    xp: Optional[list[float]] = Field(
        description="problem coordinates of the points in the x-direction",
        min_length=1,
    )
    yp: Optional[list[float]] = Field(
        description="problem coordinates of the points in the y-direction",
        min_length=1,
    )

    @model_validator(mode="after")
    def ensure_equal_size(self) -> "POINTS":
        if len(self.xp) != len(self.yp):
            raise ValueError("xp and yp must be the same size")
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"{super().cmd()}"
        for xp, yp in zip(self.xp, self.yp):
            repr += f"\nxp={xp} yp={yp}"
        return repr


class POINTS_FILE(BaseLocation):
    """Isolated output locations.

    .. code-block:: text

        POINTS 'sname' FILE 'fname'

    With this optional command the user defines a set of individual output point
    locations from text file. The file should have one point per row with x-coordinates
    and y-coordinates in the first and second columns respectively.

    Note
    ----
    All coordinates and distances should be given in m when Cartesian coordinates are
    used or degrees when Spherical coordinates are used (see command COORD).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import POINTS_FILE
        loc = POINTS_FILE(sname="outpts", fname="./output_locations.txt")
        print(loc.render())

    """

    model_type: Literal["points_file", "POINTS_FILE"] = Field(
        default="points_file", description="Model type discriminator"
    )
    fname: str = Field(
        description="Name of the file containing the output locations",
        max_length=36,
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"POINTS sname='{self.sname}' fname='{self.fname}'"
        return repr
