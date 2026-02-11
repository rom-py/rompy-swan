# Configuration Guide

This guide covers the different ways to configure SWAN simulations with rompy-swan.

## Configuration Methods

Rompy-swan supports two main configuration approaches:

1. **Python API** — Direct instantiation of components
2. **YAML/JSON** — Declarative configuration files

Both approaches produce identical results and can be mixed.

## Python API

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

### Using Dictionaries

Components accept dictionaries that are converted to subcomponents:

```python
# These are equivalent:
cgrid = REGULAR(
    spectrum=dict(mdc=36, flow=0.04, fhigh=1.0),
    grid=dict(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=100, my=50),
)

# Explicit subcomponent instantiation
from rompy_swan.subcomponents.spectrum import SPECTRUM
from rompy_swan.subcomponents.cgrid import REGULAR as REGULAR_GRID

cgrid = REGULAR(
    spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0),
    grid=REGULAR_GRID(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=100, my=50),
)
```

## YAML Configuration

### Basic Structure

```yaml
# config.yml
model_type: swan

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

startup:
  project:
    name: MySimulation
    nr: "001"
  set:
    level: 0.0
  mode:
    kind: nonstationary
    dim: twodimensional

physics:
  gen:
    model_type: gen3
  breaking:
    model_type: constant
    alpha: 1.0
    gamma: 0.73
  friction:
    model_type: jonswap
    cfjon: 0.067
```

### Loading YAML

```python
import yaml
from rompy_swan.config import SwanConfig

with open("config.yml") as f:
    config_dict = yaml.safe_load(f)

config = SwanConfig(**config_dict)
```

### Discriminated Unions

When a field accepts multiple types, use `model_type` to specify which:

```yaml
# Breaking can be CONSTANT, BKD, etc.
physics:
  breaking:
    model_type: constant  # Selects BREAKING_CONSTANT
    alpha: 1.0
    gamma: 0.73

# Or use BKD formulation
physics:
  breaking:
    model_type: bkd  # Selects BREAKING_BKD
    alpha: 1.0
    gamma0: 0.73
```

## SwanConfig Fields

| Field | Type | Description |
|-------|------|-------------|
| `cgrid` | REGULAR, CURVILINEAR, UNSTRUCTURED | Computational grid (required) |
| `startup` | STARTUP | Startup commands (PROJECT, SET, MODE, etc.) |
| `inpgrid` | INPGRIDS, DataInterface | Input grids for bathymetry, wind, etc. |
| `boundary` | BOUNDSPEC, BOUNDNEST1-3, BoundaryInterface | Boundary conditions |
| `initial` | INITIAL | Initial conditions |
| `physics` | PHYSICS | Physics commands |
| `prop` | PROP | Propagation scheme |
| `numeric` | NUMERIC | Numerical settings |
| `output` | OUTPUT | Output configuration |
| `lockup` | LOCKUP | Compute and stop commands |

## Component Groups

### STARTUP

Groups startup commands:

```python
from rompy_swan.components.group import STARTUP
from rompy_swan.components.startup import PROJECT, SET, MODE, COORDINATES

startup = STARTUP(
    project=PROJECT(name="Example", nr="001"),
    set=SET(level=0.0, depmin=0.05),
    mode=MODE(kind="nonstationary", dim="twodimensional"),
    coordinates=COORDINATES(kind="cartesian"),
)
```

### PHYSICS

Groups physics commands:

```python
from rompy_swan.components.group import PHYSICS
from rompy_swan.components.physics import GEN3, BREAKING_CONSTANT, FRICTION_JONSWAP

physics = PHYSICS(
    gen=GEN3(),
    breaking=BREAKING_CONSTANT(alpha=1.0, gamma=0.73),
    friction=FRICTION_JONSWAP(cfjon=0.067),
    triad=True,  # Enable with defaults
)
```

### INPGRIDS

Groups input grids:

```python
from rompy_swan.components.group import INPGRIDS
from rompy_swan.components.inpgrid import REGULAR

inpgrid = INPGRIDS(
    bottom=REGULAR(
        grid=dict(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=100, my=50),
        readinp=dict(fname="bottom.txt"),
    ),
    wind=REGULAR(
        grid=dict(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=10, my=5),
        readinp=dict(fname="wind.txt"),
    ),
)
```

### OUTPUT

Groups output commands:

```python
from rompy_swan.components.group import OUTPUT
from rompy_swan.components.output import BLOCK, TABLE, QUANTITY

output = OUTPUT(
    block=BLOCK(
        sname="COMPGRID",
        fname="output.nc",
        output=["hsign", "tps", "dir"],
    ),
    table=TABLE(
        sname="COMPGRID",
        fname="output.tab",
        output=["hsign", "tps"],
    ),
    quantity=[
        QUANTITY(output=["hsign"], hexp=100.0),
    ],
)
```

## Validation

Components validate parameters at construction:

```python
from rompy_swan.components.physics import BREAKING_CONSTANT

# Raises ValidationError: alpha must be positive
breaking = BREAKING_CONSTANT(alpha=-1.0, gamma=0.73)
```

Validation includes:

- **Type checking** — Correct types for each field
- **Range validation** — Values within valid ranges
- **Cross-field validation** — Consistent parameter combinations

## Environment Variables

Some settings can be configured via environment variables:

```bash
export SWAN_EXECUTABLE=/path/to/swan
```

## Best Practices

### 1. Use YAML for Reproducibility

Store configurations in version control:

```yaml
# experiments/exp001.yml
model_type: swan
cgrid: ...
physics: ...
```

### 2. Use Python for Dynamic Configuration

Generate configurations programmatically:

```python
for gamma in [0.6, 0.7, 0.8]:
    config = SwanConfig(
        physics=PHYSICS(
            breaking=BREAKING_CONSTANT(alpha=1.0, gamma=gamma),
        ),
        ...
    )
```

### 3. Validate Early

Check configurations before running:

```python
config = SwanConfig(...)
# Validation happens at construction
# If no error, configuration is valid
```

## Next Steps

- [Components](../components/index.md) — Reference for all components
- [Data Interfaces](../data-interfaces/index.md) — Connect external data
- [API Reference](../api-reference/config.md) — Complete API documentation
