"""SWAN physics components.

This package contains all physics-related components for SWAN wave model configuration.

The physics components are organized into:
- Wave generation (GEN1, GEN2, GEN3)
- Swell dissipation (NEGATINP, SSWELL_*)
- Whitecapping (WCAPPING_*)
- Quadruplet interactions (QUADRUPL)
- Wave breaking (BREAKING_*)
- Bottom friction (FRICTION_*)
- Triad interactions (TRIAD_*)
- Vegetation (VEGETATION)
- Mud (MUD)
- Sea ice (SICE_*)
- Turbulence (TURBULENCE)
- Bragg scattering (BRAGG_*)
- Limiter (LIMITER)
- Obstacles (OBSTACLE_*)
- Setup (SETUP)
- Diffraction (DIFFRACTION)
- Surfbeat (SURFBEAT)
- Scattering (SCAT)
- Deactivation (OFF, OFFS)

Private modules (prefixed with _) contain models used as field types and are not
part of the public API.
"""

# Import from completed modules
from rompy_swan.components.physics.bragg import BRAGG, BRAGG_FILE, BRAGG_FT
from rompy_swan.components.physics.breaking import BREAKING_BKD, BREAKING_CONSTANT
from rompy_swan.components.physics.diffraction import DIFFRACTION
from rompy_swan.components.physics.friction import (
    FRICTION_COLLINS,
    FRICTION_JONSWAP,
    FRICTION_MADSEN,
    FRICTION_RIPPLES,
)
from rompy_swan.components.physics.gen import GEN1, GEN2, GEN3
from rompy_swan.components.physics.limiter import LIMITER
from rompy_swan.components.physics.mud import MUD
from rompy_swan.components.physics.obstacle import OBSTACLE, OBSTACLE_FIG, OBSTACLES
from rompy_swan.components.physics.off import OFF, OFFS
from rompy_swan.components.physics.quadrupl import QUADRUPL
from rompy_swan.components.physics.scat import SCAT
from rompy_swan.components.physics.setup import SETUP
from rompy_swan.components.physics.sice import SICE, SICE_D15, SICE_M18, SICE_R19, SICE_R21B
from rompy_swan.components.physics.sswell import (
    NEGATINP,
    SSWELL_ARDHUIN,
    SSWELL_ROGERS,
    SSWELL_ZIEGER,
)
from rompy_swan.components.physics.surfbeat import SURFBEAT
from rompy_swan.components.physics.triad import TRIAD, TRIAD_DCTA, TRIAD_LTA, TRIAD_SPB
from rompy_swan.components.physics.turbulence import TURBULENCE
from rompy_swan.components.physics.vegetation import VEGETATION
from rompy_swan.components.physics.wcapping import WCAPPING_AB, WCAPPING_KOMEN

__all__ = [
    # Wave generation
    "GEN1",
    "GEN2",
    "GEN3",
    # Swell dissipation
    "NEGATINP",
    "SSWELL_ROGERS",
    "SSWELL_ARDHUIN",
    "SSWELL_ZIEGER",
    # Whitecapping
    "WCAPPING_KOMEN",
    "WCAPPING_AB",
    # Quadruplet interactions
    "QUADRUPL",
    # Wave breaking
    "BREAKING_CONSTANT",
    "BREAKING_BKD",
    # Bottom friction
    "FRICTION_JONSWAP",
    "FRICTION_COLLINS",
    "FRICTION_MADSEN",
    "FRICTION_RIPPLES",
    # Triad interactions
    "TRIAD",
    "TRIAD_DCTA",
    "TRIAD_LTA",
    "TRIAD_SPB",
    # Vegetation
    "VEGETATION",
    # Mud
    "MUD",
    # Sea ice
    "SICE",
    "SICE_R19",
    "SICE_D15",
    "SICE_M18",
    "SICE_R21B",
    # Turbulence
    "TURBULENCE",
    # Bragg scattering
    "BRAGG",
    "BRAGG_FT",
    "BRAGG_FILE",
    # Limiter
    "LIMITER",
    # Obstacles
    "OBSTACLE",
    "OBSTACLE_FIG",
    "OBSTACLES",
    # Setup
    "SETUP",
    # Diffraction
    "DIFFRACTION",
    # Surfbeat
    "SURFBEAT",
    # Scattering
    "SCAT",
    # Deactivation
    "OFF",
    "OFFS",
]
