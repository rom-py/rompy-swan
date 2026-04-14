# Rompy-SWAN Architecture

This document describes the architecture of rompy-swan, explaining how SWAN commands are organised into Python components and why this structure was chosen.

## Design Philosophy

Rompy-swan's component structure **mirrors the SWAN command file syntax**. This design makes the Python interface familiar to existing SWAN users while providing validation and discoverability for new users.

!!! note "SWAN Command Structure"
    SWAN uses a command-based input file where each line specifies a command with keywords and data. Commands must appear in a specific sequence: startup commands first, then model description (grid, input, boundary, physics, numerics), followed by output commands, and finally lock-up commands (COMPUTE, STOP). Rompy-swan enforces this ordering automatically.

### Mapping SWAN Syntax to Python

| SWAN Concept | Rompy-swan Class | Purpose |
|--------------|------------------|---------|
| Command (e.g., `GEN3`, `CGRID`) | **Component** | Represents a complete SWAN command |
| Command options with branches | **Subcomponent** | Represents options that branch into different parameter sets |
| Mutually exclusive options | **Discriminated Union** | Type-safe selection between alternatives |
| Related command groups | **Group Component** | Aggregates related components (e.g., all physics commands) |

For example, the SWAN `BOUNDSPEC` command has a `SIDE` option that accepts different parameters than the `SEGMENT` option. In rompy-swan, these are separate subcomponent classes, ensuring you only specify parameters valid for your chosen option.

```python
# SIDE and SEGMENT are different subcomponents with their own parameters
from rompy_swan.subcomponents.boundary import SIDE, SEGMENT

# Using SIDE - only side-specific parameters available
boundary = BOUNDSPEC(location=SIDE(side="west"), ...)

# Using SEGMENT - only segment-specific parameters available  
boundary = BOUNDSPEC(location=SEGMENT(ixp=0, iyp=0, ixq=10, iyq=0), ...)
```

This approach:

- **Feels familiar** to SWAN users — the structure matches the command file
- **Prevents errors** — you can't mix incompatible options
- **Enables discovery** — IDE autocomplete shows valid options for each branch

## The SwanConfig Class

The `SwanConfig` class is the main entry point. It orchestrates all SWAN commands and generates the input file.

```python
from rompy_swan.config import SwanConfig
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.startup import PROJECT, SET, MODE, COORDINATES
from rompy_swan.components.physics import GEN3, BREAKING_CONSTANT
from rompy_swan.components.group import STARTUP, PHYSICS

config = SwanConfig(
    cgrid=REGULAR(
        spectrum=dict(mdc=36, flow=0.04, fhigh=1.0),
        grid=dict(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=100, my=50),
    ),
    startup=STARTUP(
        project=PROJECT(name="Example", nr="001"),
        set=SET(level=0.0),
        mode=MODE(),
        coordinates=COORDINATES(),
    ),
    physics=PHYSICS(
        gen=GEN3(),
        breaking=BREAKING_CONSTANT(alpha=1.0, gamma=0.73),
    ),
)
```

When called, `SwanConfig` renders all components to SWAN commands:

```
PROJECT 'Example' '001'
SET level=0.0
MODE NONSTATIONARY TWODIMENSIONAL
COORDINATES CARTESIAN
CGRID REGULAR 0 0 0 100000 50000 100 50 CIRCLE 36 0.04 1.0
GEN3
BREAKING CONSTANT alpha=1.0 gamma=0.73
```

## Component Hierarchy

SWAN commands are organised into components based on their function:

```
SwanConfig
├── cgrid              # Computational grid (CGRID command)
│   ├── REGULAR        # Regular rectangular grid
│   ├── CURVILINEAR    # Curvilinear grid
│   └── UNSTRUCTURED   # Unstructured mesh
├── startup            # Startup commands (PROJECT, SET, MODE, etc.)
│   ├── project        # PROJECT command
│   ├── set            # SET command
│   ├── mode           # MODE command
│   └── coordinates    # COORDINATES command
├── inpgrid            # Input grids (INPGRID/READINP commands)
│   ├── bottom         # Bathymetry grid
│   ├── wind           # Wind forcing grid
│   ├── current        # Current forcing grid
│   └── ...            # Other input grids
├── boundary           # Boundary conditions (BOUNDSPEC, BOUNDNEST)
├── initial            # Initial conditions (INITIAL command)
├── physics            # Physics commands
│   ├── gen            # Wave generation (GEN1, GEN2, GEN3)
│   ├── breaking       # Wave breaking
│   ├── friction       # Bottom friction
│   ├── triad          # Triad interactions
│   └── ...            # Other physics
├── prop               # Propagation scheme (PROP command)
├── numeric            # Numerics (NUMERIC command)
├── output             # Output commands (BLOCK, TABLE, etc.)
└── lockup             # Lockup commands (COMPUTE, STOP)
```

## Components and Subcomponents

### Components

Components represent complete SWAN commands. Each component class corresponds to a SWAN command like `GEN3`, `CGRID`, or `BOUNDSPEC`.

```python
from rompy_swan.components.physics import GEN3, BREAKING_CONSTANT

# Each component maps to a SWAN command
gen = GEN3()                                    # -> GEN3
breaking = BREAKING_CONSTANT(alpha=1.0, gamma=0.73)  # -> BREAKING CONSTANT alpha=1.0 gamma=0.73
```

Components use a **`model_type`** field for discriminated unions, enabling instantiation from YAML/JSON configuration files.

### Subcomponents

Subcomponents represent **branching options** within SWAN commands. When a SWAN command has mutually exclusive options that each accept different parameters, these become separate subcomponent classes.

```python
from rompy_swan.components.boundary import BOUNDSPEC
from rompy_swan.subcomponents.boundary import SIDE, CONSTANTPAR

# SIDE is a subcomponent - one way to specify boundary location
# CONSTANTPAR is a subcomponent - one way to specify boundary data
boundary = BOUNDSPEC(
    shapespec=dict(model_type="jonswap", gamma=3.3),
    location=SIDE(side="west"),
    data=CONSTANTPAR(hs=2.0, per=10.0, dir=270.0, dd=30.0),
)
```

This mirrors how SWAN commands work: `BOUNDSPEC` can use `SIDE` or `SEGMENT` for location, and `PAR` or `FILE` for data. Each option has its own valid parameters.

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

## Why Components?

### 1. Validation

Components enable parameter validation before running SWAN:

```python
from rompy_swan.components.physics import BREAKING_CONSTANT

# This raises a validation error immediately
breaking = BREAKING_CONSTANT(alpha=-1.0)  # alpha must be positive
```

### 2. Discoverability

Related commands are grouped together. Need friction settings? Look in `physics.friction`:

```python
from rompy_swan.components.physics import (
    FRICTION_JONSWAP,
    FRICTION_COLLINS,
    FRICTION_MADSEN,
)
```

### 3. Type Safety

IDE autocomplete shows available options:

```python
from rompy_swan.components.cgrid import REGULAR

cgrid = REGULAR(
    spectrum=...,  # IDE shows spectrum options
    grid=...,      # IDE shows grid options
)
```

### 4. Declarative Configuration

Components can be instantiated from dictionaries (YAML/JSON):

```yaml
physics:
  gen:
    model_type: gen3
  breaking:
    model_type: constant
    alpha: 1.0
    gamma: 0.73
```

## Data Interfaces

Interface classes bridge external data with SWAN components:

### DataInterface

Connects data sources to input grids:

```python
from rompy_swan.interface import DataInterface

data = DataInterface(
    bottom=dict(
        model_type="swan_data_grid",
        source=dict(uri="bathymetry.nc"),
        var="elevation",
    ),
)
```

### BoundaryInterface

Connects spectral data to boundary conditions:

```python
from rompy_swan.interface import BoundaryInterface

boundary = BoundaryInterface(
    source=dict(uri="spectra.nc"),
    sel=dict(method="nearest"),
)
```

### OutputInterface

Configures output based on time range:

```python
from rompy_swan.interface import OutputInterface

output = OutputInterface(
    block=dict(fname="output.nc", output=["hsign", "tps"]),
)
```

## SWAN Input File Generation

`SwanConfig` handles the conversion from Python objects to SWAN input files. When you call the config, it collects all components and writes them in the correct order:

```python
config = SwanConfig(...)

# Generate the input file content
swan_input = str(config)

# Or write directly to a file
with open("INPUT", "w") as f:
    f.write(str(config))
```

!!! tip "Internal Methods"
    Components have internal `cmd()` and `render()` methods that handle command generation. You typically don't need to call these directly — `SwanConfig` manages the rendering process.

## Next Steps

- [Configuration](configuration.md) — Detailed configuration options
- [Components](../components/index.md) — Reference for all components
- [Data Interfaces](../data-interfaces/index.md) — Connect external data
