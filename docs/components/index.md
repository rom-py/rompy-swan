# Components Overview

Rompy-swan organises SWAN commands into **components** — Pydantic models that mirror the structure of SWAN commands. This design makes the Python interface familiar to existing SWAN users while providing validation and discoverability for new users.

## Design Principle

Components are modelled after the way commands are structured in the SWAN command file:

- **Commands** → **Component classes** (e.g., `GEN3`, `CGRID`, `BOUNDSPEC`)
- **Branching options** → **Subcomponent classes** (e.g., `SIDE` vs `SEGMENT` for boundary location)
- **Mutually exclusive choices** → **Discriminated unions** (type-safe selection)

This means if you know SWAN command syntax, you'll recognise the structure in rompy-swan. And if you're new to SWAN, the type validation and IDE autocomplete will guide you to valid configurations.

## Component Hierarchy

```
SwanConfig
├── cgrid              # Computational grid definition
├── startup            # Startup commands (PROJECT, SET, MODE, etc.)
├── inpgrid            # Input grids (bathymetry, wind, currents, etc.)
├── boundary           # Boundary conditions
├── initial            # Initial conditions
├── physics            # Physics commands (generation, breaking, friction, etc.)
├── prop               # Propagation scheme
├── numeric            # Numerical settings
├── output             # Output configuration
└── lockup             # Compute and stop commands
```

## Quick Reference

| Component | Purpose | Key Commands |
|-----------|---------|--------------|
| [CGRID](cgrid.md) | Computational grid | REGULAR, CURVILINEAR, UNSTRUCTURED |
| [Startup](startup.md) | Model setup | PROJECT, SET, MODE, COORDINATES |
| [INPGRID](inpgrid.md) | Input grids | INPGRID, READINP |
| [Boundary](boundary.md) | Boundary conditions | BOUNDSPEC, BOUNDNEST1-3 |
| [Physics](physics.md) | Physical processes | GEN3, BREAKING, FRICTION, TRIAD |
| [Numerics](numerics.md) | Numerical schemes | PROP, NUMERIC |
| [Output](output.md) | Output configuration | BLOCK, TABLE, SPECOUT |
| [Lockup](lockup.md) | Execution control | COMPUTE, STOP |
| [Group](group.md) | Component aggregators | STARTUP, PHYSICS, OUTPUT |

## Using Components

### Direct Instantiation

```python
from rompy_swan.config import SwanConfig
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.physics import GEN3, BREAKING_CONSTANT
from rompy_swan.components.group import PHYSICS

config = SwanConfig(
    cgrid=REGULAR(
        spectrum=dict(mdc=36, flow=0.04, fhigh=1.0),
        grid=dict(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=100, my=50),
    ),
    physics=PHYSICS(
        gen=GEN3(),
        breaking=BREAKING_CONSTANT(alpha=1.0, gamma=0.73),
    ),
)
```

### From YAML

```yaml
cgrid:
  model_type: regular
  spectrum:
    mdc: 36
    flow: 0.04
    fhigh: 1.0
  grid:
    xp: 0
    yp: 0
    alp: 0
    xlen: 100000
    ylen: 50000
    mx: 100
    my: 50

physics:
  gen:
    model_type: gen3
  breaking:
    model_type: constant
    alpha: 1.0
    gamma: 0.73
```

## Component Patterns

### Discriminated Unions

When a SWAN command has mutually exclusive options, rompy-swan uses discriminated unions with `model_type`:

```python
# Breaking can be CONSTANT or BKD - each has different parameters
from rompy_swan.components.physics import BREAKING_CONSTANT, BREAKING_BKD

# Using CONSTANT formulation
breaking = BREAKING_CONSTANT(alpha=1.0, gamma=0.73)

# Using BKD formulation  
breaking = BREAKING_BKD(alpha=1.0, gamma0=0.73, a1=0.5)
```

In YAML, use `model_type` to select which variant:

```yaml
breaking:
  model_type: constant
  alpha: 1.0
  gamma: 0.73
```

### Group Components

Group components aggregate related commands that typically appear together:

```python
from rompy_swan.components.group import PHYSICS
from rompy_swan.components.physics import GEN3, BREAKING_CONSTANT, FRICTION_JONSWAP

physics = PHYSICS(
    gen=GEN3(),
    breaking=BREAKING_CONSTANT(alpha=1.0, gamma=0.73),
    friction=FRICTION_JONSWAP(cfjon=0.067),
)
```

### Optional Components

Most components are optional with sensible defaults:

```python
# Minimal config - only cgrid is required
config = SwanConfig(
    cgrid=REGULAR(...),
)

# Add components as needed
config = SwanConfig(
    cgrid=REGULAR(...),
    physics=PHYSICS(gen=GEN3()),
    output=OUTPUT(block=BLOCK(...)),
)
```

## Subcomponents

Subcomponents represent **branching options** within SWAN commands. When a command has options that each accept different parameters, these become separate subcomponent classes:

```python
from rompy_swan.components.boundary import BOUNDSPEC
from rompy_swan.subcomponents.boundary import SIDE, CONSTANTPAR

# SIDE is one way to specify location (by domain side)
# CONSTANTPAR is one way to specify data (constant parameters)
boundary = BOUNDSPEC(
    shapespec=dict(model_type="jonswap", gamma=3.3),
    location=SIDE(side="west"),
    data=CONSTANTPAR(hs=2.0, per=10.0, dir=270.0, dd=30.0),
)
```

See the [Subcomponents](../subcomponents/base.md) section for details.

## Component Reference

Browse the component pages for detailed documentation:

- [CGRID](cgrid.md) — Computational grid definition
- [Startup](startup.md) — Model setup commands
- [INPGRID](inpgrid.md) — Input grid commands
- [Boundary](boundary.md) — Boundary condition commands
- [Physics](physics.md) — Physical process commands
- [Numerics](numerics.md) — Numerical scheme commands
- [Output](output.md) — Output configuration commands
- [Lockup](lockup.md) — Execution control commands
- [Group](group.md) — Component aggregators
