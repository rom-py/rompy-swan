"""
Startup Options
===============

This module contains option types used by startup components.

Usage
-----

Import specific option classes from their modules:

.. code-block:: python

    from rompy_swan.components.startup.options.coords import CARTESIAN, SPHERICAL

    # Use in COORDINATES component
    coords = CARTESIAN()
    coords = SPHERICAL(projection="qc")

Available Options
-----------------

**Coordinate Systems** (`coords.py`)
    - CARTESIAN - Cartesian coordinate system
    - SPHERICAL - Spherical coordinate system with projection options
"""
