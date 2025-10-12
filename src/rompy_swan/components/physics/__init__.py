"""SWAN physics commands.

This package contains SWAN physics command components organized by physical process.

Import physics modules and use them as namespaces for clarity:

Examples
--------
    # Import modules
    from rompy_swan.components.physics import friction, breaking, gen
    from rompy_swan.components.physics import scat, limiter, triad

    # Use module.Class pattern
    friction.JONSWAP(cfjon=0.038)
    breaking.CONSTANT(alpha=1.0, gamma=0.73)
    gen.GEN3(source_terms={...})
    triad.DCTA(...)

    # Single-variant commands
    scat.SCAT(iqcm=1)
    limiter.LIMITER(ursell=10.0)

For direct imports (when you only need specific classes):
    from rompy_swan.components.physics.friction import JONSWAP, MADSEN
    from rompy_swan.components.physics.breaking import CONSTANT
    from rompy_swan.components.physics.gen import GEN3

Available Modules
-----------------
bragg
    Bragg scattering: BRAGG, FT, FILE
breaking
    Wave breaking: CONSTANT, BKD
diffraction
    Diffraction: DIFFRACTION
friction
    Bottom friction: JONSWAP, COLLINS, MADSEN, RIPPLES
gen
    Wave generation: GEN1, GEN2, GEN3
limiter
    Wave height limiter: LIMITER
mud
    Mud dissipation: MUD
obstacle
    Obstacles: OBSTACLE, FIG, OBSTACLES
off
    Deactivate physics: OFF, OFFS
quadrupl
    Quadruplet interactions: QUADRUPL
scat
    Scattering: SCAT
setup
    Wave setup: SETUP
sice
    Sea ice: SICE, R19, D15, M18, R21B
sswell
    Swell dissipation: NEGATINP, ROGERS, ARDHUIN, ZIEGER
surfbeat
    Surf beat: SURFBEAT
triad
    Triad interactions: TRIAD, DCTA, LTA, SPB
turbulence
    Turbulence: TURBULENCE
vegetation
    Vegetation: VEGETATION
wcapping
    Whitecapping: WCAPPING_KOMEN, WCAPPING_AB

Options Package
---------------
For option types used by commands (e.g., ST6, JANSSEN for GEN3):
    from rompy_swan.components.physics.options.source_terms import ST6
    from rompy_swan.components.physics.options.biphase import ELDEBERKY

See `options/` package for parameter types used by commands.
"""
