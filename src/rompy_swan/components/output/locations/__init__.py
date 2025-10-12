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
"""
