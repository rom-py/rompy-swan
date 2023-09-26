"""Model output components."""
import logging
from typing import Any, Literal, Optional, Union, Annotated
from pydantic import field_validator, model_validator, Field, FieldValidationInfo

from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.output import *
from rompy.swan.subcomponents.readgrid import GRIDREGULAR


logger = logging.getLogger(__name__)


# =====================================================================================
# Locations
# =====================================================================================
class FRAME(BaseComponent):
    """Output locations on a regular grid.

    .. code-block:: text

        FRAME ’sname’ ([xpfr] [ypfr] [alpfr] [xlenfr] [ylenfr] [mxfr] [myfr])

    With this optional command the user defines output on a rectangular, uniform grid
    in a regular frame. If the set of output locations is identical to a part of the
    computational grid, then the user can use the alternative command GROUP.

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
        description="Name of the frame defined by this command", max_length=16,
    )
    grid: GRIDREGULAR = Field(description="Frame grid definition")

    @model_validator(mode="after")
    def grid_suffix(self) -> "FRAME":
        """Set expected grid suffix."""
        if self.grid.suffix != "fr":
            logger.debug(f"Set expected grid suffix 'c' instead of {self.grid.suffix}")
            self.grid.suffix = "fr"
        return self

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = f"FRAME '{self.sname}' {self.grid.render()}"
        return repr


class GROUP(BaseComponent):
    """Output locations on a regular or curvilinear grid.

    .. code-block:: text

        GROUP

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import GROUP
        loc = GROUP()
        print(loc.render())

    """
    model_type: Literal["group", "GROUP"] = Field(
        default="group", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "GROUP"
        return repr


class CURVE(BaseComponent):
    """Output locations along a curve.

    .. code-block:: text

        CURVE

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import CURVE
        loc = CURVE()
        print(loc.render())

    """
    model_type: Literal["curve", "CURVE"] = Field(
        default="curve", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "CURVE"
        return repr


class RAY(BaseComponent):
    """Output locations along a depth contour.

    .. code-block:: text

        RAY

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import RAY
        loc = RAY()
        print(loc.render())

    """
    model_type: Literal["ray", "RAY"] = Field(
        default="ray", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "RAY"
        return repr


class ISOLINE(BaseComponent):
    """Output locations along a depth contour.

    .. code-block:: text

        ISOLINE

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import ISOLINE
        loc = ISOLINE()
        print(loc.render())

    """
    model_type: Literal["isoline", "ISOLINE"] = Field(
        default="isoline", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "ISOLINE"
        return repr


class POINTS(BaseComponent):
    """Isolated output locations.

    .. code-block:: text

        POINTS

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import POINTS
        loc = POINTS()
        print(loc.render())

    """
    model_type: Literal["points", "POINTS"] = Field(
        default="points", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "POINTS"
        return repr


class NGRID(BaseComponent):
    """Output locations for a nested grid.

    .. code-block:: text

        NGRID

    Examples
    --------

    .. ipython:: python
        :okwarning:
        :okexcept:

        from rompy.swan.components.output import NGRID
        loc = NGRID()
        print(loc.render())

    """
    model_type: Literal["ngrid", "NGRID"] = Field(
        default="ngrid", description="Model type discriminator"
    )

    def cmd(self) -> str:
        """Command file string for this component."""
        repr = "NGRID"
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
FRAME_TYPE = Annotated[FRAME, Field(description="Frame locations component")]
GROUP_TYPE = Annotated[GROUP, Field(description="Group locations component")]
CURVE_TYPE = Annotated[CURVE, Field(description="Curve locations component")]
RAY_TYPE = Annotated[RAY, Field(description="Ray locations component")]
ISOLINE_TYPE = Annotated[ISOLINE, Field(description="Isoline locations component")]
POINTS_TYPE = Annotated[POINTS, Field(description="Points locations component")]
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