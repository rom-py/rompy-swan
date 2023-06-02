"""Input grid for SWAN."""
from typing import Literal
from pathlib import Path
from typing_extensions import Literal
from pydantic import root_validator

from rompy.swan.components.base import BaseComponent
from rompy.swan.subcomponents.time import NONSTATIONARY
from rompy.swan.subcomponents.readgrid import READINP
from rompy.swan.types import GridOptions


HERE = Path(__file__).parent


class INPGRID(BaseComponent):
    """SWAN input grid.

    This is the base class for all input grids. It is not meant to be used directly.

    Parameters
    ----------
    model_type: Literal["inpgrid"]
        Model type discriminator.
    grid_type: GridOptions
        Type of the swan input grid.
    excval: float | None = None
        Exception value to allow identifying and ignoring certain point inside the
        given grid during the computation. If `fac` != 1, `excval` must be given as
        `fac` times the exception value.
    nonstationary: NONSTATIONARY | None = None
        Nonstationary time specification.
    readinp: READINP
        SWAN input grid file reader.

    """

    model_type: Literal["inpgrid"] = "inpgrid"
    grid_type: GridOptions
    excval: float | None = None
    nonstationary: NONSTATIONARY | None = None
    readinp: READINP

    @root_validator
    def set_nonstat_suffix(cls, values):
        """Set the nonstationary suffix."""
        if values.get("nonstationary") is not None:
            values["nonstationary"].suffix = "inp"
        if values.get("grid_type") is not None and "grid_type" in values:
            values["readinp"].grid_type = values["grid_type"]
        return values

    def __repr__(self):
        return f"INPGRID {self.grid_type.upper()}"


class REGULAR(INPGRID):
    """SWAN regular input grid.

    Parameters
    ----------
    model_type: Literal["regular"]
        Model type discriminator.
    xpinp: float
        Geographic location (x-coordinate) of the origin of the input grid in problem
        coordinates (in m) if Cartesian coordinates are used or in degrees if spherical
        coordinates are used. In case of spherical coordinates there is no default.
    ypinp: float
        Geographic location (y-coordinate) of the origin of the input grid in problem
        coordinates (in m) if Cartesian coordinates are used or in degrees if spherical
        coordinates are used. In case of spherical coordinates there is no default.
    alpinp: float
        Direction of the positive x-axis of the input grid (in degrees, Cartesian
        convention).
    mxinp: int
        Number of meshes in x-direction of the input grid (this number is one less than
        the number of grid points in this direction).
    myinp: int
        Number of meshes in y-direction of the input grid (this number is one less than
        the number of grid points in this direction). In 1D-mode, `myinp` should be 0.
    dxinp: float
        Mesh size in x-direction of the input grid, in m in case of Cartesian
        coordinates or in degrees if spherical coordinates are used.
    dyinp: float
        Mesh size in y-direction of the input grid, in m in case of Cartesian
        coordinates or in degrees if spherical coordinates are used. In 1D-mode,
        `dyinp` may have any value.

    """
    model_type: Literal["regular"] = "regular"
    xpinp: float
    ypinp: float
    alpinp: float = 0.0
    mxinp: int
    myinp: int
    dxinp: float
    dyinp: float

    def __repr__(self):
        repr = (
            f"{super().__repr__()} REGULAR xpinp={self.xpinp} ypinp={self.ypinp} "
            f"alpinp={self.alpinp} mxinp={self.mxinp} myinp={self.myinp} "
            f"dxinp={self.dxinp} dyinp={self.dyinp}"
        )
        if self.excval is not None:
            repr += f" EXCEPTION excval={self.excval}"
        if self.nonstationary is not None:
            repr += f" {self.nonstationary.render()}"
        repr += f"\n{self.readinp.render()}"
        return repr


class CURVILINEAR(INPGRID):
    """SWAN curvilinear input grid.

    Parameters
    ----------
    model_type: Literal["curvilinear"]
        Model type discriminator.
    stagrx: float
        Staggered x'-direction with respect to computational grid, e.g., `stagrx=0.5`
        means that the input grid points are shifted a half step in x'-direction; in
        many flow models x-velocities are defined in points shifted a half step in
        x'-direction.
    stagry: float
        Staggered y'-direction with respect to computational grid, e.g., `stagry=0.5`
        means that the input grid points are shifted a half step in y'-direction; in
        many flow models y-velocities are defined in points shifted a half step in
        y'-direction.
    mxinp: int
        Number of meshes in ξ-direction of the input grid (this number is one less than
        the number of grid points in this direction). Default: `mxinp` = `mxc`.
    myinp: int
        Number of meshes in η-direction of the input grid (this number is one less than
        the number of grid points in this direction). Default: `myinp` = `myc`.

    TODO: Handle (or not) setting default values for mxinp and myinp from cgrid component in swan.

    """
    model_type: Literal["curvilinear"] = "curvilinear"
    stagrx: float = 0.0
    stagry: float = 0.0
    mxinp: int
    myinp: int

    def __repr__(self):
        repr = (
            f"{super().__repr__()} CURVILINEAR stagrx={self.stagrx} "
            f"stagry={self.stagry} mxinp={self.mxinp} myinp={self.myinp} "
        )
        if self.excval is not None:
            repr += f" EXCEPTION excval={self.excval}"
        if self.nonstationary is not None:
            repr += f" {self.nonstationary.render()}"
        return repr


class UNSTRUCTURED(INPGRID):
    """SWAN unstructured input grid.

    Parameters
    ----------
    model_type: Literal["unstructured"]
        Model type discriminator.

    """
    model_type: Literal["unstructured"] = "unstructured"

    def __repr__(self):
        repr = f"{super().__repr__()} UNSTRUCTURED"
        if self.excval is not None:
            repr += f" EXCEPTION excval={self.excval}"
        if self.nonstationary is not None:
            repr += f" {self.nonstationary.render()}"
        return repr
