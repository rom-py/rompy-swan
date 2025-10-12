"""SWAN output component."""

from abc import ABC
from typing import Annotated, Literal, Optional, Union

from pydantic import Field, field_validator, model_validator

from rompy.logging import get_logger
from rompy_swan.components.base import BaseComponent, MultiComponents
from rompy_swan.subcomponents.base import IJ, XY
from rompy_swan.subcomponents.output import ABS, REL, SPEC1D, SPEC2D
from rompy_swan.subcomponents.readgrid import GRIDREGULAR
from rompy_swan.subcomponents.time import TimeRangeOpen
from rompy_swan.types import IDLA, BlockOptions

logger = get_logger(__name__)

from rompy_swan.components.output.locations.frame import BaseLocation

SPECIAL_NAMES = ["BOTTGRID", "COMPGRID", "BOUNDARY", "BOUND_"]


class RAY(BaseComponent):
    """Output locations along a depth contour.

    .. code-block:: text

        RAY 'rname' [xp1] [yp1] [xq1] [yq1] < [int] [xp] [yp] [xq] [yq] >

    With this optional command the user provides SWAN with information to determine
    output locations along the depth contour line(s) defined subsequently in command
    `ISOLINE` (see below).

    These locations are determined by SWAN as the intersections of the depth contour
    line(s) and the set of straight rays defined in this command RAY. These rays are
    characterized by a set of master rays defined by their start and end positions
    (`xp`,`yp`) and (`xq`,`yq`). Between each pair of sequential master rays thus
    defined SWAN generates `int-1` intermediate rays by linear interpolation of the
    start and end positions.

    Rays defined by this component have nothing in common with wave rays (e.g. as
    obtained from conventional refraction computations).

    Note
    ----
    Cannot be used in 1D-mode.

    Note
    ----
    All coordinates and distances should be given in m when Cartesian coordinates are
    used or degrees when Spherical coordinates are used (see command `COORD`).

    Note
    ----
    When using rays the input grid for bottom and water level should not be curvilinear.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import RAY
        loc = RAY(
            rname="outray",
            xp1=171.9,
            yp1=-40.1,
            xq1=172.1,
            yq1=-39.9,
            npts=[3, 3],
            xp=[171.9, 173.9],
            yp=[-38.1, -38.1],
            xq=[172.1, 174.1],
            yq=[-37.9, -37.9],
        )
        print(loc.render())

    """

    model_type: Literal["ray", "RAY"] = Field(
        default="ray", description="Model type discriminator"
    )
    rname: str = Field(
        description="Name of the set of rays defined by this command",
        max_length=32,
    )
    xp1: float = Field(
        description=(
            "Problem coordinate of the begin point of the first master ray "
            "in the x-direction"
        ),
    )
    yp1: float = Field(
        description=(
            "Problem coordinate of the begin point of the first master ray "
            "in the y-direction"
        ),
    )
    xq1: float = Field(
        description=(
            "Problem coordinate of the end point of the first master ray "
            "in the x-direction"
        ),
    )
    yq1: float = Field(
        description=(
            "Problem coordinate of the end point of the first master ray "
            "in the y-direction"
        ),
    )
    npts: list[int] = Field(
        description=(
            "The `int` RAY parameter, number of subdivisions between the previous "
            "master ray and the following master ray defined by the following data "
            "(number of subdivisions is one morethan the number of interpolated rays)"
        ),
        min_length=1,
    )
    xp: list[float] = Field(
        description=(
            "problem coordinates of the begin of each subsequent master ray in the "
            "x-direction"
        ),
        min_length=1,
    )
    yp: list[float] = Field(
        description=(
            "problem coordinates of the begin of each subsequent master ray in the "
            "y-direction"
        ),
        min_length=1,
    )
    xq: list[float] = Field(
        description=(
            "problem coordinates of the end of each subsequent master ray in the "
            "x-direction"
        ),
        min_length=1,
    )
    yq: list[float] = Field(
        description=(
            "problem coordinates of the end of each subsequent master ray in the "
            "y-direction"
        ),
        min_length=1,
    )

    @model_validator(mode="after")
    def ensure_equal_size(self) -> "CURVE":
        for key in ["xp", "yp", "xq", "yq"]:
            if len(getattr(self, key)) != len(self.npts):
                raise ValueError(f"Size of npts and {key} must be the same")
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"RAY rname='{self.rname}'"
        repr += f" xp1={self.xp1} yp1={self.yp1} xq1={self.xq1} yq1={self.yq1}"
        for npts, xp, yp, xq, yq in zip(self.npts, self.xp, self.yp, self.xq, self.yq):
            repr += f"\nint={npts} xp={xp} yp={yp} xq={xq} yq={yq}"
        return repr
