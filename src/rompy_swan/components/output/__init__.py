"""
SWAN Output Components
======================

This module contains components for configuring output locations and parameters
for SWAN model results, including spatial points, curves, and nested grids.

Usage
-----

Import specific component classes from their submodules:

.. code-block:: python

    # Location components
    from rompy_swan.components.output.locations.frame import FRAME
    from rompy_swan.components.output.locations.points import POINTS
    from rompy_swan.components.output.locations.ngrid import NGRID
    
    # Settings components
    from rompy_swan.components.output.settings.quantity import QUANTITY
    from rompy_swan.components.output.settings.options import OUTPUT_OPTIONS
    
    # Write components
    from rompy_swan.components.output.write.block import BLOCK
    from rompy_swan.components.output.write.table import TABLE

Available Components
--------------------

**Locations** (`locations/`)
    - FRAME - Output on regular grid
    - GROUP - Output on subset of grid
    - CURVE, CURVES - Output along curve(s)
    - RAY - Output along depth contour
    - ISOLINE - Output along depth contour
    - POINTS, POINTS_FILE - Isolated output locations
    - NGRID, NGRID_UNSTRUCTURED - Nested grid output

**Settings** (`settings/`)
    - QUANTITY, QUANTITIES - Define output settings
    - OUTPUT_OPTIONS - Set format of output

**Write** (`write/`)
    - BLOCK, BLOCKS - Write spatial distributions
    - TABLE - Write table output
    - SPECOUT - Write wave spectra
    - NESTOUT - Write 2D boundary spectra

**Test** (`test.py`)
    - TEST - Write intermediate results

**Options** (`options/`)
    - ABS, REL - Output specification types
    - SPEC1D, SPEC2D - Spectral output types
"""

# Special names constant
SPECIAL_NAMES = ["BOTTGRID", "COMPGRID", "BOUNDARY", "BOUND_"]

# For backward compatibility - re-export all classes
# This allows existing code like `from rompy_swan.components.output import FRAME` to work
from rompy_swan.components.output.locations.curve import CURVE, CURVES
from rompy_swan.components.output.locations.frame import BaseLocation, FRAME
from rompy_swan.components.output.locations.group import GROUP
from rompy_swan.components.output.locations.isoline import ISOLINE
from rompy_swan.components.output.locations.ngrid import NGRID, NGRID_UNSTRUCTURED
from rompy_swan.components.output.locations.points import POINTS, POINTS_FILE
from rompy_swan.components.output.locations.ray import RAY
from rompy_swan.components.output.settings.options import OUTPUT_OPTIONS
from rompy_swan.components.output.settings.quantity import QUANTITIES, QUANTITY
from rompy_swan.components.output.test import TEST
from rompy_swan.components.output.write.block import BLOCK, BLOCKS
from rompy_swan.components.output.write.nestout import NESTOUT
from rompy_swan.components.output.write.specout import SPECOUT
from rompy_swan.components.output.write.table import TABLE

__all__ = [
    # Constants
    "SPECIAL_NAMES",
    # Base classes
    "BaseLocation",
    # Locations
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
    # Settings
    "QUANTITY",
    "QUANTITIES",
    "OUTPUT_OPTIONS",
    # Write
    "BLOCK",
    "BLOCKS",
    "TABLE",
    "SPECOUT",
    "NESTOUT",
    # Test
    "TEST",
]
