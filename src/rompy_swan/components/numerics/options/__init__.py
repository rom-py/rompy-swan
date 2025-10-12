"""
Numerics Options
================

This module contains option types used by numerics components.

Usage
-----

Import specific option classes from this module:

.. code-block:: python

    from rompy_swan.components.numerics.options import BSBT, GSE, STOPC, ACCUR

    # Use in PROP component
    prop = BSBT()
    prop = GSE(waveage=dict(delt=86400, dfmt="day"))

Available Options
-----------------

**Propagation Schemes**
    - BSBT - First order propagation scheme
    - GSE - Garden-sprinkler effect counteraction

**Stopping Criteria**
    - STOPC - Stopping criteria (Zijlema and Van der Westhuysen, 2005)
    - ACCUR - Stop the iterative procedure (obsolete in SWAN 41.01)

**Numerical Schemes**
    - DIRIMPL - Numerical scheme for refraction
    - SIGIMPL - Frequency shifting accuracy
    - CTHETA - Prevents excessive directional turning
    - CSIGMA - Prevents excessive frequency shifting
    - SETUP - Stop criteria in wave setup computation

**Computation Parameters**
    - STAT - Stationary computation parameters
    - NONSTAT - Nonstationary computation parameters
"""

# Re-export from subcomponents for now (will be moved later)
from rompy_swan.subcomponents.numerics import (
    ACCUR,
    BSBT,
    CSIGMA,
    CTHETA,
    DIRIMPL,
    GSE,
    NONSTAT,
    SETUP,
    SIGIMPL,
    STAT,
    STOPC,
)

__all__ = [
    "BSBT",
    "GSE",
    "STAT",
    "NONSTAT",
    "STOPC",
    "ACCUR",
    "DIRIMPL",
    "SIGIMPL",
    "CTHETA",
    "CSIGMA",
    "SETUP",
]
