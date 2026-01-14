# Physics

SWAN physics commands control the physical processes in wave simulations. These include wave generation by wind, energy dissipation (whitecapping, bottom friction, depth-induced breaking), and nonlinear wave-wave interactions.

!!! tip "Default Physics"
    By default, SWAN activates third-generation physics (`GEN3`) which includes wind input, whitecapping, quadruplet interactions, and bottom friction. You can selectively disable processes using the `OFF` commands or customize individual formulations.

## Generation

::: rompy_swan.components.physics.GEN1
::: rompy_swan.components.physics.GEN2
::: rompy_swan.components.physics.GEN3

## Swell dissipation

::: rompy_swan.components.physics.NEGATINP
::: rompy_swan.components.physics.SSWELL_ARDHUIN
::: rompy_swan.components.physics.SSWELL_ZIEGER
::: rompy_swan.components.physics.SSWELL_ROGERS

## Whitecapping

::: rompy_swan.components.physics.WCAPPING_KOMEN
::: rompy_swan.components.physics.WCAPPING_AB

## Quadruplet interactions

::: rompy_swan.components.physics.QUADRUPL

## Wave breaking

::: rompy_swan.components.physics.BREAKING_CONSTANT
::: rompy_swan.components.physics.BREAKING_BKD

## Bottom friction

::: rompy_swan.components.physics.FRICTION_JONSWAP
::: rompy_swan.components.physics.FRICTION_COLLINS
::: rompy_swan.components.physics.FRICTION_MADSEN
::: rompy_swan.components.physics.FRICTION_RIPPLES

## Wave triads

::: rompy_swan.components.physics.TRIAD
::: rompy_swan.components.physics.TRIAD_DCTA
::: rompy_swan.components.physics.TRIAD_LTA
::: rompy_swan.components.physics.TRIAD_SPB

## Vegetation damping

::: rompy_swan.components.physics.VEGETATION

## Mud damping

::: rompy_swan.components.physics.MUD

## Sea ice dissipation

::: rompy_swan.components.physics.SICE
::: rompy_swan.components.physics.SICE_R19
::: rompy_swan.components.physics.SICE_D15
::: rompy_swan.components.physics.SICE_M18
::: rompy_swan.components.physics.SICE_R21B

## Turbulent viscosity

::: rompy_swan.components.physics.TURBULENCE

## Bragg scattering

::: rompy_swan.components.physics.BRAGG
::: rompy_swan.components.physics.BRAGG_FT
::: rompy_swan.components.physics.BRAGG_FILE

## Limiter

::: rompy_swan.components.physics.LIMITER

## Obstacle

::: rompy_swan.components.physics.OBSTACLE
::: rompy_swan.components.physics.OBSTACLE_FIG
::: rompy_swan.components.physics.OBSTACLES

## Wave setup

::: rompy_swan.components.physics.SETUP

## Wave diffraction

::: rompy_swan.components.physics.DIFFRACTION

## Surfbeat

::: rompy_swan.components.physics.SURFBEAT

## Scattering

::: rompy_swan.components.physics.SCAT

## Off

::: rompy_swan.components.physics.OFF
::: rompy_swan.components.physics.OFFS