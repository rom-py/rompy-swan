"""
Output Components
=================

This module contains components for defining output in SWAN.

Usage
-----

Import specific output classes from their modules:

.. code-block:: python

    # Location components
    from rompy_swan.components.output.frame import FRAME
    from rompy_swan.components.output.points import POINTS
    from rompy_swan.components.output.curve import CURVE
    
    # Write components
    from rompy_swan.components.output.block import BLOCK
    from rompy_swan.components.output.table import TABLE
    from rompy_swan.components.output.specout import SPECOUT
    
    # Settings components
    from rompy_swan.components.output.quantity import QUANTITY
    from rompy_swan.components.output.options import OUTPUT_OPTIONS

Available Components
--------------------

**Output Locations** - Define where to output
    - FRAME - Output on regular grid
    - GROUP - Output on subset of grid
    - CURVE, CURVES - Output along curves
    - RAY - Output along depth contour
    - ISOLINE - Output along depth contour
    - POINTS, POINTS_FILE - Isolated output locations
    - NGRID, NGRID_UNSTRUCTURED - Output for nested grids

**Write Components** - Define how to write output
    - BLOCK, BLOCKS - Write spatial distributions
    - TABLE - Write table output
    - SPECOUT - Write wave spectra
    - NESTOUT - Write 2D boundary spectra for nested runs

**Settings Components** - Configure output settings
    - QUANTITY, QUANTITIES - Define output quantities
    - OUTPUT_OPTIONS - Set output format options
    - TEST - Test output points

Base Classes
------------

This module also defines abstract base classes for output components:

.. code-block:: python

    from rompy_swan.components.output import BaseLocation, BaseWrite
"""

from abc import ABC
from typing import Literal, Optional

from pydantic import Field, field_validator, model_validator

from rompy_swan.components.base import BaseComponent
from rompy_swan.subcomponents.time import TimeRangeOpen

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

        from rompy_swan.components.output import BaseLocation
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


class BaseWrite(BaseComponent, ABC):
    """Base class for SWAN output writing.

    .. code-block:: text

        {MODEL_TYPE} sname='sname'

    This is the base class for all write components. It is not meant to be used
    directly.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.output import BaseWrite
        write = BaseWrite(
            sname="outgrid",
            fname="./output-grid.nc",
            times=dict(
                tbeg="2012-01-01T00:00:00",
                delt="PT30M",
                tfmt=1,
                dfmt="min",
                suffix="",
            )
        )
        print(write.render())

    """

    model_type: Literal["write", "WRITE"] = Field(
        default="write",
        description="Model type discriminator",
    )
    sname: str = Field(
        description=(
            "Name of the set of output locations in which the output is to be written"
        ),
        max_length=8,
    )
    fname: str = Field(
        description=(
            "Name of the data file where the output is written to The file format is "
            "defined by the file extension, use `.mat` for MATLAB binary (single "
            "precision) or `.nc` for netCDF format. If any other extension is used "
            "the ASCII format is assumed"
        ),
    )
    times: Optional[TimeRangeOpen] = Field(
        default=None,
        description=(
            "Time specification if the user requires output at various times. If this "
            "option is not specified data will be written for the last time step of "
            "the computation"
        ),
    )

    @model_validator(mode="after")
    def validate_special_names(self) -> "BaseWrite":
        special_names = ("COMPGRID", "BOTTGRID")
        snames = self.sname if isinstance(self.sname, list) else [self.sname]
        for sname in snames:
            if sname in special_names and self.model_type.upper() != "BLOCK":
                raise ValueError(f"Special name {sname} is only supported with BLOCK")
        return self

    @model_validator(mode="after")
    def validate_times(self) -> "BaseWrite":
        if self.times is not None:
            self.times.suffix = self.suffix
        return self

    @property
    def suffix(self) -> str:
        return ""

    def cmd(self) -> str:
        """Command file string for this component."""
        return ""


# Import all output components for convenience
from rompy_swan.components.output.block import BLOCK, BLOCKS
from rompy_swan.components.output.curve import CURVE, CURVES
from rompy_swan.components.output.frame import FRAME
from rompy_swan.components.output.group import GROUP
from rompy_swan.components.output.isoline import ISOLINE
from rompy_swan.components.output.nestout import NESTOUT
from rompy_swan.components.output.ngrid import NGRID, NGRID_UNSTRUCTURED
from rompy_swan.components.output.options import OUTPUT_OPTIONS
from rompy_swan.components.output.points import POINTS, POINTS_FILE
from rompy_swan.components.output.quantity import QUANTITIES, QUANTITY
from rompy_swan.components.output.ray import RAY
from rompy_swan.components.output.specout import SPECOUT
from rompy_swan.components.output.table import TABLE
from rompy_swan.components.output.test import TEST

__all__ = [
    # Base classes
    "BaseLocation",
    "BaseWrite",
    # Location components
    "FRAME",
    "GROUP",
    "CURVE",
    "CURVES",
    "RAY",
    "ISOLINE",
    "POINTS",
    "POINTS_FILE",
    "NGRID",
    "NGRID_UNSTRUCTURED",
    # Write components
    "BLOCK",
    "BLOCKS",
    "TABLE",
    "SPECOUT",
    "NESTOUT",
    # Settings components
    "QUANTITY",
    "QUANTITIES",
    "OUTPUT_OPTIONS",
    "TEST",
]
