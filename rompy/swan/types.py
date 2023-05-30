"""Types for the swan wrapper."""
from enum import Enum


class GridOptions(str, Enum):
    """Valid options for the input grid type."""
    bottom = "bottom"
    wlevel = "wlevel"
    current = "current"
    vx = "vx"
    vy = "vy"
    wind = "wind"
    wx = "wx"
    wy = "wy"
    friction = "friction"
    nplants = "nplants"
    turbvisc = "turbvisc"
    mudlayer = "mudlayer"
    aice = "aice"
    hice = "hice"
    hss = "hss"
    tss = "tss"