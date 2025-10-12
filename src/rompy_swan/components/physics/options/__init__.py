"""Physics option types for SWAN commands.

This package contains the various option types (parameter models) used by SWAN physics
commands. These classes define the different ways to specify parameters for commands
like GEN3, TRIAD, OBSTACLE, etc.

Users should import directly from the specific modules:

Examples
--------
    from rompy_swan.components.physics.options.source_terms import ST6, JANSSEN
    from rompy_swan.components.physics.options.biphase import ELDEBERKY
    from rompy_swan.components.physics.options.transmission import TRANSM, GODA
    from rompy_swan.components.physics.options.reflection import REFL, FREEBOARD

For most use cases, you can use dict-based configuration instead of importing these
directly:

Examples
--------
    from rompy_swan.components.physics import GEN3

    # Dict-based (YAML-friendly)
    gen = GEN3(source_terms={"model_type": "st6", "a1sds": 4.75e-7, "a2sds": 7.0e-5})

    # Or direct instantiation
    from rompy_swan.components.physics.options.source_terms import ST6
    gen = GEN3(source_terms=ST6(a1sds=4.75e-7, a2sds=7.0e-5))

Modules
-------
source_terms
    Source term options for GEN3 command (JANSSEN, KOMEN, WESTHUYSEN, ST6, etc.)
biphase
    Biphase options for TRIAD command (ELDEBERKY, DEWIT)
transmission
    Transmission options for OBSTACLE command (TRANSM, GODA, DANGREMOND, etc.)
reflection
    Reflection options for OBSTACLE command (REFL, RSPEC, RDIFF, FREEBOARD, LINE)
"""
