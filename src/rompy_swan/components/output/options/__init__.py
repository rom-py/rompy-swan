"""
Output Options
==============

This module contains option types used by output components.

Usage
-----

Import specific option classes:

.. code-block:: python

    from rompy_swan.components.output.options import ABS, REL, SPEC1D, SPEC2D

Available Options
-----------------

**Output Specification** (from `subcomponents.output`)
    - ABS - Absolute output specification
    - REL - Relative output specification
    - SPEC1D - 1D spectral output
    - SPEC2D - 2D spectral output
"""

# Re-export from subcomponents for now (will be moved later)
from rompy_swan.subcomponents.output import ABS, REL, SPEC1D, SPEC2D

__all__ = ["ABS", "REL", "SPEC1D", "SPEC2D"]
