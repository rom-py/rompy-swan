"""
Output Write Components
=======================

This module contains components for writing SWAN output to files.

Usage
-----

Import specific write classes from their modules:

.. code-block:: python

    from rompy_swan.components.output.write.block import BLOCK
    from rompy_swan.components.output.write.table import TABLE
    from rompy_swan.components.output.write.specout import SPECOUT

Available Write Components
--------------------------

**Spatial Distributions** (`block.py`)
    - BLOCK - Write spatial distributions
    - BLOCKS - Write multiple spatial distributions

**Table Output** (`table.py`)
    - TABLE - Write table output

**Spectral Output** (`specout.py`)
    - SPECOUT - Write wave spectra

**Nested Output** (`nestout.py`)
    - NESTOUT - Write 2D boundary spectra for nested runs
"""
