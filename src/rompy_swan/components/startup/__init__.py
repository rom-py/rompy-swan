"""
SWAN Startup Components
=======================

This module contains components for initializing and configuring SWAN model runs,
including project settings, coordinate systems, and run modes.

Usage
-----

Import specific component classes from their modules:

.. code-block:: python

    from rompy_swan.components.startup.project import PROJECT
    from rompy_swan.components.startup.set import SET
    from rompy_swan.components.startup.mode import MODE
    from rompy_swan.components.startup.coordinates import COORDINATES

    # Use components
    project = PROJECT(nr="001", name="Test")
    set_cmd = SET(level=0.0, direction_convention="nautical")
    mode = MODE(kind="nonstationary", dim="twodimensional")
    coords = COORDINATES()

Available Components
--------------------

**Project Configuration** (`project.py`)
    - PROJECT - Define project identification and titles

**Settings** (`set.py`)
    - SET - Configure general SWAN parameters

**Run Mode** (`mode.py`)
    - MODE - Set stationary/nonstationary and 1D/2D mode

**Coordinate System** (`coordinates.py`)
    - COORDINATES - Choose between Cartesian and spherical coordinates

**Options** (`options/`)
    - CARTESIAN, SPHERICAL - Coordinate system types
"""
