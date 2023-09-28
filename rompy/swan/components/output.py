"""Model output components."""
import logging
from typing import Any, Literal, Optional, Union, Annotated
from pydantic import field_validator, model_validator, Field, FieldValidationInfo

from rompy.swan.types import BlockOptions, IDLA
from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.readgrid import GRIDREGULAR
from rompy.swan.subcomponents.time import TIME


logger = logging.getLogger(__name__)


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


class NGRID_UNSTRUCTURED(BaseComponent):
    """Output locations for a nested grid.

    .. code-block:: text

        NGRID 'sname' UNSTRUCTURED ->TRIANGLE|EASYMESH 'fname'

    If the user wishes to carry out nested SWAN runs, a separate coarse-grid SWAN run
    is required. With this optional command `NGRID`, the user defines in the present
    coarse-grid run, a set of output locations along the boundary of the subsequent
    nested computational grid. The set of output locations thus defined is of the type
    NGRID.

    With this option the user indicates that the subsequent nested grid is unstructured
    Only grids generated by Triangle and Easymesh are supported by SWAN.

    Note
    ----
    Command `NESTOUT` is required after this command `NGRID` to generate some data for
    the (subsequent) nested run.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import NGRID_UNSTRUCTURED
        loc = NGRID_UNSTRUCTURED(kind="triangle", fname="ngrid.txt")
        print(loc.render())

    """
    model_type: Literal["ngrid_unstructured", "NGRID_UNSTRUCTURED"] = Field(
        default="ngrid_unstructured", description="Model type discriminator"
    )
    kind: Optional[Literal["triangle", "easymesh"]] = Field(
        default="triangle",
        description=(
            "Indicate if nested grid is generated by Triangle or Easymesh. The base "
            "name of the grid specified in the `fname` parameter is used internally "
            "by SWAN to define the `.node` and `.ele` files in case of the former or "
            "the `.n` and `.e` files in case of the latter."
        ),
    )
    fname: str = Field(
        description="Basename of the required files, i.e. without extension",
        max_length=32,
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"NGRID UNSTRUCTURED {self.kind} fname='{self.fname}'"
        return repr


# =====================================================================================
# Write / plot
# =====================================================================================
class QUANTITY(BaseComponent):
    """Define output settings.

    .. code-block:: text

        QUANTITY [output1 ...] 'short' 'long' [lexp] [hexp] [excv] [power] [ref] &
            [fswell] [fmin] [fmax] ->PROBLEMCOORD|FRAME

        Examples:
        ---------
        QUANTITY Xp hexp=100.
        QUANTITY HS TM01 RTMM10 excv=-9.
        QUANTITY HS TM02 FSPR fmin=0.03 fmax=0.5
        QUANTITY Hswell fswell=0.08
        QUANTITY Per short='Tm-1,0' power=0.
        QUANTITY Transp Force Frame

    With this command the user can influence:

    * The naming of output quantities
    * The accuracy of writing output quantities
    * The definition of some output quantities
    * Reference direction for vectors

    Note
    ----
    The following data are accepted only in combination with some specific quantities:

    * power
    * ref
    * fswell
    * fmin
    * fmax
    * PROBLEMCOORD
    * FRAME

    Note
    ----
    **PROBLEMCOORD**: Vector components are relative to the x- and y-axes of the
    problem coordinate system (see command `SET`):

    - Directions are counterclockwise relative to the positive x-axis of the problem
      coordinate system if Cartesian direction convention is used.
    - Directions are relative to North (clockwise) if Nautical direction convention is
      used.

    Note
    ----
    **FRAME**: If output is requested on sets created by command FRAME or
    automatically (see command `SET`) (`COMPGRID` or `BOTTGRID`):

    - Vector components are relative to the x- and y-axes of the frame coordinate
    system.
    - Directions are counterclockwise relative to the positive x-axis of the frame
    coordinate system if Cartesian direction convention is used.
    - Directions are relative to North (clockwise) if Nautical direction convention
    is used.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import QUANTITY
        quant = QUANTITY(output=["xp"], hexp=100)
        print(quant.render())
        quant = QUANTITY(output=["hsign", "tm01", "rtmm10"], excv=-9)
        print(quant.render())
        quant = QUANTITY(output=["hsign", "tm02", "fspr"], fmin=0.03, fmax=0.5)
        print(quant.render())
        quant = QUANTITY(output=["hsign"], fswell=0.08)
        print(quant.render())
        quant = QUANTITY(output=["per"], short="Tm-1,0", power=0)
        print(quant.render())
        quant = QUANTITY(output=["transp", "force"], coord="frame")
        print(quant.render())

    """
    model_type: Literal["quantity", "QUANTITY"] = Field(
        default="quantity", description="Model type discriminator"
    )
    output: list[BlockOptions] = Field(
        description="The output variables to define settings for",
        min_length=1,
    )
    short: Optional[str] = Field(
        default=None,
        description=(
            "Short name of the output quantity (e.g. the name in the heading of a "
            "table written by SWAN). If this option is not used, SWAN will use a "
            "realistic name"
        ),
        max_length=16,
    )
    long: Optional[str] = Field(
        default=None,
        description=(
            "Long name of the output quantity (e.g. the name in the heading of a "
            "block output written by SWAN). If this option is not used, SWAN will "
            "use a realistic name"
        ),
        max_length=16,
    )
    lexp: Optional[float] = Field(
        default=None,
        description="Lowest expected value of the output quantity",
    )
    hexp: Optional[float] = Field(
        default=None,
        description=(
            "Highest expected value of the output quantity; the highest expected "
            "value is used by SWAN to determine the number of decimals in a table "
            "with heading. So the `QUANTITY` command can be used in case the default "
            "number of decimals in a table is unsatisfactory"
        ),
    )
    excv: Optional[float] = Field(
        default=None,
        description=(
            "In case there is no valid value (e.g. wave height in a dry point) this "
            "exception value is written in a table or block output"
        ),
    )
    power: Optional[float] = Field(
        default=None,
        description=(
            "power `p` appearing in the definition of `PER`, `RPER` and `WLEN`. Note "
            "that the value for `power` given for `PER` affects also the value of "
            "`RPER`; the power for `WLEN` is independent of that of `PER` or `RPER` "
            "(SWAN default: 1)"
        ),
    )
    ref: Optional[str] = Field(
        default=None,
        description=(
            "Reference time used for the quantity `TSEC`. Default value: starting "
            "time of the first computation, except in cases where this is later than "
            "the time of the earliest input. In these cases, the time of the earliest "
            "input is used"
        ),
    )
    fswell: Optional[float] = Field(
        default=None,
        description=(
            "Upper limit of frequency range used for computing the quantity HSWELL "
            "(SWAN default: 0.1 Hz)"
        ),
    )
    noswll: Optional[int] = Field(
        default=None,
        description=(
            "Number of swells to output for watershed quantities "
        ),
    )
    fmin: Optional[float] = Field(
        default=None,
        description=(
            "Lower limit of frequency range used for computing integral parameters "
            "(SWAN Default: 0.0 Hz)"
        ),
    )
    fmax: Optional[float] = Field(
        default=None,
        description=(
            "Upper limit of frequency range used for computing integral parameters "
            "(SWAN default: 1000.0 Hz, acts as infinity)"
        ),
    )
    coord: Optional[Literal["problemcoord", "frame"]] = Field(
        default=None,
        description=(
            "Define if vectors and directions refer to the problem coordinate system "
            "('problemcoord') or sets created by command FRAME ('frame') "
            "(SWAN default: problemcoord)"
        ),
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "QUANTITY"
        for output in self.quantities:
            repr += f" {output.upper()}"
        if self.short is not None:
            repr += f" short='{self.short}'"
        if self.long is not None:
            repr += f" long='{self.long}'"
        if self.lexp is not None:
            repr += f" lexp={self.lexp}"
        if self.hexp is not None:
            repr += f" hexp={self.hexp}"
        if self.excv is not None:
            repr += f" excv={self.excv}"
        if self.power is not None:
            repr += f" power={self.power}"
        if self.ref is not None:
            repr += f" ref='{self.ref}'"
        if self.fswell is not None:
            repr += f" fswell={self.fswell}"
        if self.noswll is not None:
            repr += f" noswll={self.noswll}"
        if self.fmin is not None:
            repr += f" fmin={self.fmin}"
        if self.fmax is not None:
            repr += f" fmax={self.fmax}"
        if self.coord is not None:
            repr += f" {self.coord.upper()}"
        return repr


class OUTPUT_OPTIONS(BaseComponent):
    """Set format of output.

    .. code-block:: text

        OUTPUT OPTIons 'comment' (TABLE [field]) (BLOCK [ndec] [len]) (SPEC [ndec])

    This command enables the user to influence the format of block, table and spectral
    output.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import OUTPUT_OPTIONS
        opts = OUTPUT_OPTIONS(
            comment="!", field=10, ndec_block=4, len=20, ndec_spec=6,
        )
        print(opts.render())

    """
    model_type: Literal["block", "BLOCK"] = Field(
        default="block", description="Model type discriminator"
    )
    comment: Optional[str] = Field(
        default=None,
        description=(
            "Comment character used in comment lines in the output (SWAN default: %)"
        ),
        min_length=1,
        max_length=1,
    )
    field: Optional[int] = Field(
        default=None,
        description="Length of one data field in a table (SWAN default: 12)",
        ge=8,
        le=16,
    )
    ndec_block: Optional[int] = Field(
        default=None,
        description="Number of decimals in block output (SWAN default: 4)",
        ge=0,
        le=9,
    )
    len: Optional[int] = Field(
        default=None,
        description="Number of data on one line of block output (SWAN default: 6)",
        ge=1,
        le=9999,
    )
    ndec_spec: Optional[int] = Field(
        default=None,
        description="Number of decimals in spectra output (SWAN default: 4)",
        ge=0,
        le=9,
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "OUTPUT OPTIONS"
        if self.comment is not None:
            repr += f" comment='{self.comment}'"
        if self.field is not None:
            repr += f" TABLE field={self.field}"
        if self.ndec_block is not None or self.len is not None:
            repr += f" BLOCK"
            if self.ndec_block is not None:
                repr += f" ndec={self.ndec_block}"
            if self.len is not None:
                repr += f" len={self.len}"
        if self.ndec_spec is not None:
            repr += f" SPEC ndec={self.ndec_spec}"
        return repr


class BLOCK(BaseComponent):
    """Write spatial distributions.

    .. code-block:: text

        BLOCK 'sname' ->HEADER|NOHEADER 'fname' (LAYOUT [idla]) [output1 ...] &
            [unit] (OUTPUT [tbegblk] [deltblk]) SEC|MIN|HR|DAY

    With this optional command the user indicates that one or more spatial
    distributions should be written to a file.

    Note
    ----
    The text of the header indicates run identification (see command `PROJECT`), time,
    frame or group name ('sname'), variable and unit. The number of header lines is 8.

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import BLOCK
        block = BLOCK(sname="outgrid", fname="./depth-frame.nc", output=["depth"])
        print(block.render())
        block = BLOCK(
            sname="COMPGRID",
            header=False,
            fname="./output-grid.nc",
            idla=3,
            output=["hsign", "hswell", "dir", "tps", "tm01", "watlev", "qp"],
            time=dict(tbeg="2012-01-01T00:00:00", delt="PT30M", deltfmt="min"),
        )
        print(block.render())

    """
    model_type: Literal["block", "BLOCK"] = Field(
        default="block", description="Model type discriminator"
    )
    sname: str = Field(
        description=(
            "Name of the frame in which the output is to be written to including one "
            "of the SWAN special frames 'BOTTGRID' or 'COMPGRID'"
        ),
    )
    header: Optional[bool] = Field(
        default=None,
        description=(
            "Indicate if the output should be written to a file with header lines "
            "(SWAN default: True)"
        ),
    )
    fname: str = Field(
        description=(
            "Name of the data file where the output is to be written to. The file "
            "format is defined by the file extension, use `.mat` for MATLAB binary "
            "(single precision) or `.nc` for netCDF format. If any other extension is "
            "used the ASCII format is assumed"
        ),
    )
    idla: Optional[IDLA] = Field(
        default=None,
        description=(
            "Prescribe the lay-out of the output to file (supported options here are "
            "1, 3, 4). Option 4 is recommended for postprocessing an ASCII file by "
            "MATLAB, however option 3 is recommended in case of binary MATLAB output "
            "(SWAN default: 1)"
        ),
    )
    output: list[BlockOptions] = Field(
        description="The output variables to output to block file",
        min_length=1,
    )
    unit: Optional[float] = Field(
        default=None,
        description=(
            "Controls the scaling of the output. The program divides computed values "
            "by `unit` before writing to file, so the user should multiply the "
            "written value by `unit` to obtain the proper value. By default, if "
            "HEADER is selected, value is written as a 5 position integer. SWAN takes "
            "`unit` such that the largest number occurring in the block can be "
            "printed. If NOHEADER is selected, values are printed in floating-point "
            "format by default (`unit=1`)"
        ),
    )
    time: Optional[TIME] = Field(
        default=None,
        description=(
            "Time specification if the user requires output at various times. If this "
            "option is not specified block will be written for the last time step of "
            "the computation"
        ),
    )

    @model_validator(mode="after")
    def idla_validator(self) -> "BLOCK":
        """Validate IDLA."""
        if self.idla not in (1, 3, 4, None):
            raise ValueError(
                f"Only IDLA options (1, 3, 4) are supported in BLOCK, got {self.idla}"
            )
        if self.fname.endswith(".mat") and self.idla != 3:
            logger.warning(
                "MATLAB binary output requested, `idla=3` is recommended "
                f"(idla={self.idla} set)."
            )
        return self

    @model_validator(mode="after")
    def time_suffix(self) -> "BLOCK":
        """Set expected time suffix."""
        if self.time is not None:
            self.time.suffix = "blk"
            if self.time.tend is not None:
                logger.warning(
                    "Time specification `tend` is not supported in BLOCK ignoring"
                )
                self.time.tend = None
        return self

    @property
    def _header(self) -> str:
        """Render the header instruction."""
        if self.header:
            return "HEADER"
        else:
            return "NOHEADER"

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"BLOCK sname='{self.sname}'"
        if self.header is not None:
            repr += f" {self._header}"
        repr += f" fname='{self.fname}'"
        if self.idla is not None:
            repr += f" LAYOUT idla={self.idla}"
        for output in self.output:
            if len(self.output) > 1:
                repr += "\n"
            else:
                repr += " "
            repr += f"{output.upper()}"
        if self.unit is not None:
            repr += f"\nunit={self.unit}"
        if self.time is not None:
            repr += f"\nOUTPUT {self.time.render()}"
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
NGRID_TYPE = Annotated[
    Union[NGRID, NGRID_UNSTRUCTURED], Field(description="Ngrid locations component")
]

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