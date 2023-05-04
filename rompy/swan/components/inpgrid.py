"""Input grid for SWAN."""
import yaml
from enum import Enum
from typing import Literal
from enum import Enum
from pathlib import Path
from typing_extensions import Literal
from pydantic import root_validator

from rompy.swan.components.base import BaseComponent, NONSTATIONARY


HERE = Path(__file__).parent


class InpgridOptions(str, Enum):
    """Valid options for the input grid type."""
    bottom = "bottom"
    wlevel = "wlevel"
    current = "current"
    vx = "vx"
    vy = "vy"
    friction = "friction"
    wind = "wind"
    wx = "wx"
    wy = "wy"
    nplants = "nplants"
    turbvisc = "turbvisc"
    mudlayer = "mudlayer"
    aice = "aice"
    hice = "hice"
    hss = "hss"
    tss = "tss"


class INPGRID(BaseComponent):
    """SWAN input grid.

    This is the base class for all input grids. It is not meant to be used directly.

    Parameters
    ----------
    kind : Literal["inpgrid"]
        Name of the component to help parsing and render as a comment in the cmd file.
    inpgrid: InpgridOptions
    excval: float | None = None
        Exception value to allow identifying and ignoring certain point inside the
        given grid during the computation. If `fac` != 1, `excval` must be given as
        `fac` times the exception value.
    nonstationary: NONSTATIONARY | None = None
        Nonstationary time specification.

    """

    kind: Literal["inpgrid"] = "inpgrid"
    inpgrid: InpgridOptions
    excval: float | None = None
    nonstationary: NONSTATIONARY | None = None

    @root_validator
    def set_nonstat_suffix(cls, values):
        """Set the nonstationary suffix."""
        if values.get("nonstationary") is not None:
            values["nonstationary"].suffix = "inp"
        return values

    def __repr__(self):
        return f"INPGRID {self.inpgrid.upper()}"


class REGULAR(INPGRID):
    """SWAN regular input grid.

    Parameters
    ----------
    kind : Literal["regular"]
        Name of the component to help parsing and render as a comment in the cmd file.
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
        than the number of grid points in this direction).
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
    kind: Literal["regular"] = "regular"
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
        return repr


class CURVILINEAR(INPGRID):
    pass


class UNSTRUCTURED(INPGRID):
    pass


from typing import List


class Regular(BaseComponent):
    xpinp: float
    ypinp: float
    alpinp: float
    mxinp: float
    myinp: float
    dxinp: float
    dyinp: float


class Curvilinear(BaseComponent):
    stagrx: List[float]
    stagry: List[float]
    mxinp: float
    myinp: float


class Exception(BaseComponent):
    excval: float


class NonStationary(BaseComponent):
    tbeginp: float
    deltinp: float
    min: float
    tendinp: float


class INPGrid(BaseComponent):
    bottom: str
    wlevel: str
    current: str
    vx: str
    vy: str
    friction: str
    wind: str
    wx: str
    wy: str
    nplants: str
    turbvisc: str
    mudlayer: str
    aice: str
    hice: str
    hss: str
    tss: str
    regular: Regular = None
    curvilinear: Curvilinear = None
    unstructured: str = None
    exception: Exception = None
    nonstationary: NonStationary = None
