# Quickstart

This guide walks you through creating a basic SWAN simulation with rompy-swan.

## Basic Workflow

1. Define the computational grid (CGRID)
2. Configure startup parameters (project, mode, coordinates)
3. Set up input grids for bathymetry, wind, etc.
4. Configure physics (wave generation, breaking, friction)
5. Define boundary conditions
6. Configure output
7. Generate the model and run

## Minimal Example

```python
from datetime import datetime
from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_swan.config import SwanConfig
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.startup import PROJECT, SET, MODE, COORDINATES
from rompy_swan.components.physics import GEN3, BREAKING_CONSTANT, FRICTION_JONSWAP
from rompy_swan.components.numerics import NUMERIC
from rompy_swan.components.group import STARTUP, PHYSICS

# 1. Define the computational grid
cgrid = REGULAR(
    spectrum=dict(mdc=36, flow=0.04, fhigh=1.0),
    grid=dict(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=100, my=50),
)

# 2. Configure startup
startup = STARTUP(
    project=PROJECT(name="MySimulation", nr="001"),
    set=SET(level=0.0),
    mode=MODE(),
    coordinates=COORDINATES(),
)

# 3. Configure physics
physics = PHYSICS(
    gen=GEN3(),
    breaking=BREAKING_CONSTANT(alpha=1.0, gamma=0.73),
    friction=FRICTION_JONSWAP(cfjon=0.067),
)

# 4. Create the config
config = SwanConfig(
    cgrid=cgrid,
    startup=startup,
    physics=physics,
)

# 5. Create and run the model
model = ModelRun(
    run_id="my_swan_run",
    period=TimeRange(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 2),
    ),
    config=config,
)

# Generate input files
model.generate()

# Run SWAN (requires swan executable)
# model.run()
```

## Using YAML Configuration

For reproducibility, define your configuration in YAML:

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
  coordinates:
    kind: cartesian

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

Load and use:

```python
import yaml
from rompy_swan.config import SwanConfig

with open("config.yml") as f:
    config_dict = yaml.safe_load(f)

config = SwanConfig(**config_dict)
```

## Adding Input Grids

SWAN requires input grids for bathymetry and optionally for wind, currents, and other forcing:

```python
from rompy_swan.components.inpgrid import REGULAR as INPGRID_REGULAR
from rompy_swan.components.group import INPGRIDS

inpgrid = INPGRIDS(
    bottom=INPGRID_REGULAR(
        grid=dict(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=100, my=50),
        readinp=dict(fname="bottom.txt"),
    ),
    wind=INPGRID_REGULAR(
        grid=dict(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=10, my=5),
        readinp=dict(fname="wind.txt"),
    ),
)

config = SwanConfig(
    cgrid=cgrid,
    startup=startup,
    inpgrid=inpgrid,
    physics=physics,
)
```

## Adding Boundary Conditions

For wave boundary conditions from spectral data:

```python
from rompy_swan.components.boundary import BOUNDSPEC
from rompy_swan.subcomponents.boundary import SIDE, CONSTANTPAR

boundary = BOUNDSPEC(
    shapespec=dict(model_type="jonswap", gamma=3.3),
    location=SIDE(side="west"),
    data=CONSTANTPAR(hs=2.0, per=10.0, dir=270.0, dd=30.0),
)

config = SwanConfig(
    cgrid=cgrid,
    startup=startup,
    boundary=boundary,
    physics=physics,
)
```

## Configuring Output

```python
from rompy_swan.components.output import BLOCK, QUANTITY
from rompy_swan.components.group import OUTPUT

output = OUTPUT(
    block=BLOCK(
        model_type="block",
        sname="COMPGRID",
        fname="output.nc",
        output=["hsign", "tps", "dir", "depth"],
    ),
    quantity=[
        QUANTITY(output=["hsign"], hexp=100.0),
    ],
)

config = SwanConfig(
    cgrid=cgrid,
    startup=startup,
    physics=physics,
    output=output,
)
```

## Complete Example with Data Interface

For connecting to external data sources:

```python
from rompy_swan.interface import DataInterface, BoundaryInterface

# Use DataInterface for automatic data handling
data = DataInterface(
    bottom=dict(
        model_type="swan_data_grid",
        source=dict(uri="bathymetry.nc"),
        var="elevation",
    ),
    wind=dict(
        model_type="swan_data_grid",
        source=dict(uri="wind.nc"),
        var=["u10", "v10"],
    ),
)

config = SwanConfig(
    cgrid=cgrid,
    startup=startup,
    inpgrid=data,
    physics=physics,
)
```

## Next Steps

- [Architecture](../user-guide/architecture.md) — Understand the component structure
- [Configuration](../user-guide/configuration.md) — Detailed configuration options
- [Components](../components/index.md) — Reference for all components
- [Data Interfaces](../data-interfaces/index.md) — Connect external data sources
