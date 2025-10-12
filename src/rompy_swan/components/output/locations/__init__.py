"""
Output Locations
================

This module contains components for defining output locations in SWAN.

Usage
-----

Import specific location classes from their modules:

.. code-block:: python

    from rompy_swan.components.output.locations.frame import FRAME
    from rompy_swan.components.output.locations.points import POINTS
    from rompy_swan.components.output.locations.ngrid import NGRID

Available Locations
-------------------

**Regular Grids** (`frame.py`)
    - FRAME - Output on regular grid

**Grid Subsets** (`group.py`)
    - GROUP - Output on subset of grid

**Curves** (`curve.py`)
    - CURVE - Output along a curve
    - CURVES - Output along multiple curves

**Depth Contours** (`ray.py`, `isoline.py`)
    - RAY - Output along depth contour
    - ISOLINE - Output along depth contour

**Points** (`points.py`)
    - POINTS - Isolated output locations
    - POINTS_FILE - Isolated output locations from file

**Nested Grids** (`ngrid.py`)
    - NGRID - Output for nested grid
    - NGRID_UNSTRUCTURED - Output for unstructured nested grid

Base Classes
------------

This package also defines the abstract base class `BaseLocation` that all location
components inherit from. Import it directly from this package:

.. code-block:: python

    from rompy_swan.components.output.locations import BaseLocation
"""

from abc import ABC
from typing import Literal

from pydantic import Field, field_validator

from rompy_swan.components.base import BaseComponent

SPECIAL_NAMES = ["BOTTGRID", "COMPGRID", "BOUNDARY", "BOUND_"]


class BaseLocation(BaseComponent, ABC):
    """Base class for SWAN output locations.

    .. code-block:: text

        {MODEL_TYPE} sname='sname'

    This is the base class for all locations components. It is not meant to be used
    directly.

    Note
    ----
    The name of the set of output locations `sname` cannot be longer than 8 characters
    and must not match any SWAN special names such as `BOTTGRID` (define output over
    the bottom/current grid) or `COMPGRID` (define output over the computational grid).

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output.locations import BaseLocation
        loc = BaseLocation(sname="outsites")
        print(loc.render())

    """

    model_type: Literal["locations", "LOCATIONS"] = Field(
        default="locations",
        description="Model type discriminator",
    )
    sname: str = Field(
        description="Name of the set of output locations defined by this command",
        max_length=8,
    )

    @field_validator("sname")
    @classmethod
    def not_special_name(cls, sname: str) -> str:
        """Ensure sname is not defined as one of the special names."""
        for name in SPECIAL_NAMES:
            if sname.upper().startswith(name):
                raise ValueError(f"sname {sname} is a special name and cannot be used")
        return sname

    def cmd(self) -> str:
        """Command file string for this component."""
        return f"{self.model_type.upper()} sname='{self.sname}'"
