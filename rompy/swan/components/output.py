"""Model output components."""
import logging
from typing import Any, Literal, Optional, Union, Annotated
from pydantic import field_validator, model_validator, Field, FieldValidationInfo

from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.output import *
from rompy.swan.subcomponents.readgrid import GRIDREGULAR


logger = logging.getLogger(__name__)


# TODO: Ensure 'BOTTGRID' and 'COMPGRID' are accepted in place of FRAME
# TODO 'BOUNDARY' and 'BOUND_0N' are accepted in appropriate write commands
# TODO: Allow setting float precision where appropriate

# =====================================================================================
# Locations
# =====================================================================================
class FRAME(BaseComponent):
    """Output locations on a regular grid.

    .. code-block:: text

        FRAME 'sname' [xpfr] [ypfr] [alpfr] [xlenfr] [ylenfr] [mxfr] [myfr]

    With this optional command the user defines output on a rectangular, uniform grid
    in a regular frame. If the set of output locations is identical to a part of the
    computational grid, then the user can use the alternative command GROUP.

    Note
    ----
    Cannot be used in 1D-mode.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import FRAME
        loc = FRAME(
            sname="outgrid",
            grid=dict(xp=173, yp=-40, xlen=2, ylen=2, mx=19, my=19),
        )
        print(loc.render())

    """
    model_type: Literal["frame", "FRAME"] = Field(
        default="frame", description="Model type discriminator"
    )
    sname: str = Field(
        description="Name of the frame defined by this command", max_length=32,
    )
    grid: GRIDREGULAR = Field(description="Frame grid definition")

    @model_validator(mode="after")
    def grid_suffix(self) -> "FRAME":
        """Set expected grid suffix."""
        self.grid.suffix = "fr"
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"FRAME sname='{self.sname}' {self.grid.render()}"
        return repr


class GROUP(BaseComponent):
    """Output locations on a regular or curvilinear grid.

    .. code-block:: text

        GROUP 'sname' SUBGRID [ix1] [ix2] [iy1] [iy2]

    With this optional command the user defines a group of output locations on a
    rectangular or curvilinear grid that is identical with (part of) the computational
    grid (rectilinear or curvilinear). Such a group may be convenient for the user to
    obtain output that is not affected by interpolation errors.

    The subgrid contains those points (ix,iy) of the computational grid for which:
    `ix1` <= `ix` <= `ix2` and `iy1` <= `iy` <= `iy2 (The origin of the computational
    grid is `ix=0`, `iy=0`)`

    Note
    ----
    Command **CGRID** should precede this command **GROUP**.

    Note
    ----
    Cannot be used in 1D-mode or in case of unstructured grids.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import GROUP
        loc = GROUP(sname="outsubgrid", ix1=20, iy1=0, ix2=50, iy2=100)
        print(loc.render())

    """
    model_type: Literal["group", "GROUP"] = Field(
        default="group", description="Model type discriminator"
    )
    sname: str = Field(
        description="Name of the set of output locations defined by this command",
        max_length=32,
    )
    ix1: int = Field(
        description="Lowest index of the computational grid in the ix-direction",
    )
    iy1: int = Field(
        description="Lowest index of the computational grid in the iy-direction",
    )
    ix2: int = Field(
        description="Highest index of the computational grid in the ix-direction",
    )
    iy2: int = Field(
        description="Highest index of the computational grid in the ix-direction",
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"GROUP sname='{self.sname}'"
        repr += f" SUBGRID ix1={self.ix1} iy1={self.iy1} ix2={self.ix2} iy2={self.iy2}"
        return repr


class CURVE(BaseComponent):
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
        :okexcept:

        from rompy.swan.components.output import CURVE
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
    sname: str = Field(
        description="Name of the set of output locations defined by this command",
        max_length=32,
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
        repr = f"CURVE sname='{self.sname}' xp1={self.xp1} yp1={self.yp1}"
        for npts, xp, yp in zip(self.npts, self.xp, self.yp):
            repr += f"\nint={npts} xp={xp} yp={yp}"
        return repr


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

    Note
    ----
    All coordinates and distances should be given in m when Cartesian coordinates are
    used or degrees when Spherical coordinates are used (see command COORD).

    Note
    ----
    Rays defined by this component have nothing in common with wave rays (e.g. as
    obtained from conventional refraction computations).

    Note
    ----
    When using rays the input grid for bottom and water level should not be curvilinear.

    Note
    ----
    Cannot be used in 1D-mode.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import RAY
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
        repr = f"CURVE rname='{self.rname}'"
        repr += f" xp1={self.xp1} yp1={self.yp1} xq1={self.xq1} yq1={self.yq1}"
        for npts, xp, yp, xq, yq in zip(self.npts, self.xp, self.yp, self.xq, self.yq):
            repr += f"\nint={npts} xp={xp} yp={yp} xq={xq} yq={yq}"
        return repr


class ISOLINE(BaseComponent):
    """Output locations along a depth contour.

    .. code-block:: text

        ISOLINE 'sname' 'rname' DEPTH|BOTTOM [dep]

    With this optional command the user defines a set of output locations along one
    depth or bottom level contour line (in combination with command RAY).

    Note
    ----
    Cannot be used in 1D-mode.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import ISOLINE
        loc = ISOLINE(sname="outcurve", rname="outray", dep_type="depth", dep=12.0)
        print(loc.render())

    """
    model_type: Literal["isoline", "ISOLINE"] = Field(
        default="isoline", description="Model type discriminator"
    )
    sname: str = Field(
        description="Name of the set of output locations defined by this command",
        max_length=32,
    )
    rname: str = Field(
        description="Name of the set of rays defined by this command",
        max_length=32,
    )
    dep: float = Field(
        description=(
            "The depth (in m) of the depth contour line along which output locations "
            "are generated by SWAN."
        ),
    )
    dep_type: Optional[Literal["depth", "bottom"]] = Field(
        default=None,
        description=(
            "Define if the depth contour is extracted from the DEPTH output (the "
            "stationary water depth) or from the BOTTOM output (the depth relative "
            "to the datum level with the water level ignored) (SWAN default: DEPTH)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"ISOLINE sname='{self.sname}' rname='{self.rname}'"
        if self.dep_type is not None:
            repr += f" {self.dep_type.upper()}"
        repr += f" dep={self.dep}"
        return repr


class POINTS(BaseComponent):
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
        :okexcept:

        from rompy.swan.components.output import POINTS
        loc = POINTS(sname="outpoints", xp=[172.3, 172.4], yp=[-39, -39])
        print(loc.render())

    """
    model_type: Literal["points", "POINTS"] = Field(
        default="points", description="Model type discriminator"
    )
    sname: str = Field(
        description="Name of the set of output locations defined by this command",
        max_length=32,
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
            raise ValueError(f"xp and yp must be the same size")
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"POINTS sname='{self.sname}'"
        for xp, yp in zip(self.xp, self.yp):
            repr += f"\nxp={xp} yp={yp}"
        return repr


class POINTS_FILE(BaseComponent):
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
        :okexcept:

        from rompy.swan.components.output import POINTS_FILE
        loc = POINTS_FILE(sname="outpoints", fname="./output_locations.txt")
        print(loc.render())

    """
    model_type: Literal["points_file", "POINTS_FILE"] = Field(
        default="points_file", description="Model type discriminator"
    )
    sname: str = Field(
        description="Name of the set of output locations defined by this command",
        max_length=32,
    )
    fname: str = Field(
        description="Name of the file containing the output locations",
        max_length=110,
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"POINTS sname='{self.sname}' fname='{self.fname}'"
        return repr


class NGRID(BaseComponent):
    """Output locations for a nested grid.

    .. code-block:: text

        NGRID 'sname' [xpn] [ypn] [alpn] [xlenn] [ylenn] [mxn] [myn]

    If the user wishes to carry out nested SWAN runs, a separate coarse-grid SWAN run
    is required. With this optional command `NGRID`, the user defines in the present
    coarse-grid run, a set of output locations along the boundary of the subsequent
    nested computational grid. The set of output locations thus defined is of the type
    NGRID.

    Note
    ----
    Command `NESTOUT` is required after this command `NGRID` to generate some data for
    the (subsequent) nested run.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import NGRID
        loc = NGRID(
            sname="outgrid",
            grid=dict(xp=173, yp=-40, xlen=2, ylen=2, mx=19, my=19),
        )
        print(loc.render())

    """
    model_type: Literal["ngrid", "NGRID"] = Field(
        default="ngrid", description="Model type discriminator"
    )
    sname: str = Field(
        description=(
            "name of the set of output locations along the boundaries of the "
            "following nested computational grid defined by this command"
        ),
        max_length=32,
    )
    grid: GRIDREGULAR = Field(description="NGRID grid definition")

    @model_validator(mode="after")
    def grid_suffix(self) -> "FRAME":
        """Set expected grid suffix."""
        self.grid.suffix = "n"
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"NGRID {self.grid.render()}"
        return repr


# =====================================================================================
# Write / plot
# =====================================================================================
class BLOCK(BaseComponent):
    """Write spatial distributions.

    .. code-block:: text

        BLOCK

    Note
    ----
    Only for FRAME and GROUP.

    Note
    ----
    Cannot be used in 1D-mode.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import BLOCK
        out = BLOCK()
        print(out.render())

    """
    model_type: Literal["block", "BLOCK"] = Field(
        default="block", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "BLOCK"
        return repr


class TABLE(BaseComponent):
    """Write output for output locations.

    .. code-block:: text

        TABLE

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import TABLE
        out = TABLE()
        print(out.render())

    """
    model_type: Literal["block", "TABLE"] = Field(
        default="block", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "TABLE"
        return repr


class SPECOUT(BaseComponent):
    """Write to data file the wave spectra.

    .. code-block:: text

        SPECOUT

    Write to data file the variance / energy density spectrum for output locations.

    Note
    ----
    See command SET for definition of variance or energy density.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import SPECOUT
        out = SPECOUT()
        print(out.render())

    """
    model_type: Literal["specout", "SPECOUT"] = Field(
        default="specout", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "SPECOUT"
        return repr


class NESTOUT(BaseComponent):
    """Write to 2D boundary spectra.

    .. code-block:: text

        NESTOUT

    Write to data file two-dimensional action density spectra (relative frequency)
    along the boundary of a nested grid (see command NGRID) to be used in a subsequent
    SWAN run.

    Note
    ----
    See command SET for definition of variance or energy density.

    Note
    ----
    Cannot be used in 1D-mode.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import NESTOUT
        out = NESTOUT()
        print(out.render())

    """
    model_type: Literal["nestout", "NESTOUT"] = Field(
        default="nestout", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "NESTOUT"
        return repr


# =====================================================================================
# Output group component
# =====================================================================================
# GEN_TYPE = Annotated[
#     Union[GEN1, GEN2, GEN3],
#     Field(description="Wave generation component", discriminator="model_type"),
# ]

# TODO: CURVE should be a list type

FRAME_TYPE = Annotated[FRAME, Field(description="Frame locations component")]
GROUP_TYPE = Annotated[GROUP, Field(description="Group locations component")]
CURVE_TYPE = Annotated[CURVE, Field(description="Curve locations component")]
RAY_TYPE = Annotated[RAY, Field(description="Ray locations component")]
ISOLINE_TYPE = Annotated[ISOLINE, Field(description="Isoline locations component")]
POINTS_TYPE = Annotated[
    Union[POINTS, POINTS_FILE],
    Field(description="Points locations component", discriminator="model_type"),
]
NGRID_TYPE = Annotated[NGRID, Field(description="Frame locations component")]

BLOCK_TYPE = Annotated[BLOCK, Field(description="Block write component")]
TABLE_TYPE = Annotated[TABLE, Field(description="Table write component")]
SPECOUT_TYPE = Annotated[SPECOUT, Field(description="Spectra write component")]
NESTOUT_TYPE = Annotated[NESTOUT, Field(description="Spectra write component")]

class OUTPUT(BaseComponent):
    """Output group component.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import OUTPUT
        out = OUTPUT()
        print(out.render())

    """
    model_type: Literal["output", "OUTPUT"] = Field(
        default="output", description="Model type discriminator"
    )
    frame: Optional[FRAME_TYPE] = Field(default=None)
    group: Optional[GROUP_TYPE] = Field(default=None)
    curve: Optional[CURVE_TYPE] = Field(default=None)
    ray: Optional[RAY_TYPE] = Field(default=None)
    isoline: Optional[ISOLINE_TYPE] = Field(default=None)
    points: Optional[POINTS_TYPE] = Field(default=None)
    ngrid: Optional[NGRID_TYPE] = Field(default=None)
    block: Optional[BLOCK_TYPE] = Field(default=None)
    table: Optional[TABLE_TYPE] = Field(default=None)
    specout: Optional[SPECOUT_TYPE] = Field(default=None)
    nestout: Optional[NESTOUT_TYPE] = Field(default=None)

    @model_validator(mode="after")
    def block_only_with_frame_or_group(self) -> "OUTPUT":
        """Ensure Block is only defined for FRAME and GROUP locations."""
        return self

    @model_validator(mode="after")
    def isoline_ray_defined(self) -> "OUTPUT":
        """Ensure the isoline ray has been defined."""
        if self.isoline is not None:
            if self.ray is None:
                raise ValueError(
                    f"Isoline {self.isoline} requires RAY rname='{self.isoline.rname}'"
                    " but no RAY component has been defined"
                )
            elif self.ray.rname != self.isoline.rname:
                raise ValueError(
                    f"Isoline rname='{self.isoline.rname}' does not match "
                    f"the ray rname='{self.ray.rname}'"
                )
        return self

    @model_validator(mode="after")
    def ngrid_and_nestout(self) -> "OUTPUT":
        """Ensure NGRID and NESTOUT are specified together."""
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = []
        if self.frame is not None:
            repr += [f"{self.frame.render()}"]
        if self.group is not None:
            repr += [f"{self.group.render()}"]
        if self.curve is not None:
            repr += [f"{self.curve.render()}"]
        if self.ray is not None:
            repr += [f"{self.ray.render()}"]
        if self.isoline is not None:
            repr += [f"{self.isoline.render()}"]
        if self.points is not None:
            repr += [f"{self.points.render()}"]
        if self.ngrid is not None:
            repr += [f"{self.ngrid.render()}"]
        if self.block is not None:
            repr += [f"{self.block.render()}"]
        if self.table is not None:
            repr += [f"{self.table.render()}"]
        if self.specout is not None:
            repr += [f"{self.specout.render()}"]
        if self.nestout is not None:
            repr += [f"{self.nestout.render()}"]
        return repr