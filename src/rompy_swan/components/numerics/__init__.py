"""
SWAN Numerics Components
=========================

This module contains components for configuring the numerical schemes and parameters
used in SWAN for wave propagation, frequency shifting, and other numerical aspects.

Usage
-----

Import specific component classes from their modules:

.. code-block:: python

    from rompy_swan.components.numerics.prop import PROP
    from rompy_swan.components.numerics.numeric import NUMERIC

    # Use components
    prop = PROP(scheme=dict(model_type="bsbt"))
    numeric = NUMERIC(stop=dict(model_type="stopc", dabs=0.05))

Available Components
--------------------

**Propagation Scheme** (`prop.py`)
    - PROP - Configure wave propagation scheme (BSBT, GSE)

**Numerical Parameters** (`numeric.py`)
    - NUMERIC - Configure numerical schemes and stopping criteria

**Options** (`options/`)
    - BSBT - First order propagation scheme
    - GSE - Garden-sprinkler effect counteraction
    - STOPC - Stopping criteria (Zijlema and Van der Westhuysen, 2005)
    - ACCUR - Stop the iterative procedure (obsolete)
    - DIRIMPL - Numerical scheme for refraction
    - SIGIMPL - Frequency shifting accuracy
    - CTHETA - Prevents excessive directional turning
    - CSIGMA - Prevents excessive frequency shifting
    - SETUP - Stop criteria in wave setup computation
"""

# For backward compatibility - re-export from specific modules
from rompy_swan.components.numerics.numeric import NUMERIC
from rompy_swan.components.numerics.prop import PROP

__all__ = ["PROP", "NUMERIC"]
