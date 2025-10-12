"""SWAN output component."""

from typing import Literal

from pydantic import Field, model_validator

from rompy_swan.components.base import BaseComponent
from rompy_swan.components.output import BaseLocation


class CURVE(BaseLocation):
    """Output locations along a curve.

    .. code-block:: text

        CURVE 'sname' [xp1] [yp1] < [int] [xp] [yp] >

    With this optional command the user defines output along a curved line. Actually
    this curve is a broken line, defined by the user with its corner points. The values
    of the output quantities along the curve are interpolated from the computational
    grid. This command may be used more than once to define more curves.

    Note
    ----
    The following pre-defined curves are available and could be used instead of a CURVE
    component: 'BOUNDARY' and `BOUND_0N` where `N` is boundary part number.

    Note
    ----
    All coordinates and distances should be given in m when Cartesian coordinates are
    used or degrees when Spherical coordinates are used (see command COORD).

    Note
    ----
    Repeat the group `< int xp yp` > in proper order if there are more corner points
    on the curve.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import CURVE
        loc = CURVE(
            sname="outcurve",
            xp1=172,
            yp1=-40,
            npts=[3, 3],
            xp=[172.0, 174.0],
            yp=[-38.0, -38.0],
        )
        print(loc.render())

    """

    model_type: Literal["curve", "CURVE"] = Field(
        default="curve", description="Model type discriminator"
    )
    xp1: float = Field(
        description=(
            "Problem coordinate of the first point of the curve in the x-direction"
        ),
    )
    yp1: float = Field(
        description=(
            "Problem coordinate of the first point of the curve in the y-direction"
        ),
    )
    npts: list[int] = Field(
        description=(
            "The `int` CURVE parameter, SWAN will generate `npts-1` equidistant "
            "locations between two subsequent corner points of the curve "
            "including the two corner points"
        ),
        min_length=1,
    )
    xp: list[float] = Field(
        description=(
            "problem coordinates of a corner point of the curve in the x-direction"
        ),
        min_length=1,
    )
    yp: list[float] = Field(
        description=(
            "problem coordinates of a corner point of the curve in the y-direction"
        ),
        min_length=1,
    )

    @model_validator(mode="after")
    def ensure_equal_size(self) -> "CURVE":
        for key in ["xp", "yp"]:
            if len(getattr(self, key)) != len(self.npts):
                raise ValueError(f"Size of npts and {key} must be the same")
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"{super().cmd()} xp1={self.xp1} yp1={self.yp1}"
        for npts, xp, yp in zip(self.npts, self.xp, self.yp):
            repr += f"\nint={npts} xp={xp} yp={yp}"
        return repr


class CURVES(BaseComponent):
    """Output locations along multiple curves.

    .. code-block:: text

        CURVE 'sname1' [xp1] [yp1] < [int] [xp] [yp] >
        CURVE 'sname2' [xp1] [yp1] < [int] [xp] [yp] >
        ..

    This component can be used to prescribe and render multiple CURVE components.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import CURVE, CURVES
        loc1 = CURVE(
            sname="c1", xp1=7, yp1=-40, npts=[3, 3], xp=[7, 9], yp=[-38, -38],
        )
        loc2 = CURVE(
            sname="c2", xp1=3, yp1=-37, npts=[5, 5], xp=[4, 5], yp=[-37, -36],
        )
        locs = CURVES(curves=[loc1, loc2])
        print(locs.render())

    """

    model_type: Literal["curves", "CURVES"] = Field(
        default="curves", description="Model type discriminator"
    )
    curves: list[CURVE] = Field(description="CURVE components")

    @property
    def sname(self) -> list[str]:
        return [curve.sname for curve in self.curves]

    def cmd(self) -> list[str]:
        repr = []
        for curve in self.curves:
            repr += [curve.cmd()]
        return repr
