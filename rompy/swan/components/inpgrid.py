"""Input grid for SWAN."""
import yaml
from typing import Literal
from enum import Enum
from pathlib import Path
from typing_extensions import Literal

from rompy.swan.components.base import BaseComponent


HERE = Path(__file__).parent

# Define valid options for the input grid type including upper and lower case versions
inpgrid_options = [
    "BOTtom",
    "WLEVel",
    "CURrent",
    "VX",
    "VY",
    "FRiction",
    "WInd",
    "WX",
    "WY",
    "NPLAnts",
    "TURBvisc",
    "MUDLayer",
    "AICE",
    "HICE",
    "HSS",
    "TSS",
]
inpgrid_options += ["".join(c for c in s if c.isupper()) for s in inpgrid_options]
inpgrid_options += [option.upper() for option in inpgrid_options]
inpgrid_options += [option.lower() for option in inpgrid_options]


class INPGRID(BaseComponent):
    """SWAN input grid.

    Parameters
    ----------
    kind : Literal["INPGRID"]
        Name of the component to help parsing and render as a comment in the cmd file.

    """

    kind: Literal["INPGRID"] | Literal["INP"] | Literal["inpgrid"] = "INPGRID"
    inpgrid: Literal[tuple(inpgrid_options)]

    def __repr__(self):
        return "INPGRID"


class REGULAR(INPGRID):
    pass


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
