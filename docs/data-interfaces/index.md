# Data Interfaces Overview

Rompy-swan provides **data interfaces** to connect external data sources with SWAN model inputs. These interfaces handle:

- **Data loading** — Read from NetCDF, THREDDS, local files
- **Interpolation** — Regrid data to SWAN computational grids
- **File generation** — Write SWAN-compatible input files
- **Time handling** — Extract data for simulation periods

## Interface Types

| Interface | Purpose | Use Case |
|-----------|---------|----------|
| [DataInterface](data.md) | Input grids | Bathymetry, wind, currents from data sources |
| [BoundaryInterface](boundary.md) | Boundary conditions | Spectral wave data at boundaries |
| [OutputInterface](output.md) | Output configuration | Configure output based on time range |
| [LockupInterface](lockup.md) | Execution control | Configure compute commands |

## DataInterface

The `DataInterface` connects external data sources to SWAN input grids (INPGRID commands).

### Basic Usage

```python
from rompy_swan.interface import DataInterface

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
    inpgrid=data,  # Use DataInterface instead of INPGRIDS
    ...
)
```

### Supported Input Types

- **bottom** — Bathymetry
- **wind** — Wind forcing (u, v components)
- **current** — Current forcing (u, v components)
- **wlevel** — Water level
- **ice** — Ice coverage
- **friction** — Spatially varying friction
- **mud** — Mud properties
- **vegetation** — Vegetation properties

### Data Sources

DataInterface supports various data sources:

```python
# Local NetCDF file
source=dict(uri="data.nc")

# Remote THREDDS/OPeNDAP
source=dict(uri="https://thredds.server.com/data.nc")

# With specific reader
source=dict(
    model_type="intake",
    catalog="catalog.yml",
    dataset="bathymetry",
)
```

## BoundaryInterface

The `BoundaryInterface` connects spectral wave data to SWAN boundary conditions.

### Basic Usage

```python
from rompy_swan.interface import BoundaryInterface

boundary = BoundaryInterface(
    source=dict(uri="spectra.nc"),
    sel=dict(method="nearest"),
    location=dict(model_type="side", side="west"),
)

config = SwanConfig(
    cgrid=cgrid,
    boundary=boundary,
    ...
)
```

### Spectral Data

BoundaryInterface expects spectral data with:

- **freq** — Frequency dimension
- **dir** — Direction dimension
- **efth** — Energy density spectrum

### Location Options

```python
# Entire side
location=dict(model_type="side", side="west")

# Segment
location=dict(model_type="segment", ...)

# Points
location=dict(model_type="points", xp=[...], yp=[...])
```

## OutputInterface

The `OutputInterface` configures output based on the simulation time range.

### Basic Usage

```python
from rompy_swan.interface import OutputInterface

output = OutputInterface(
    block=dict(
        fname="output.nc",
        output=["hsign", "tps", "dir"],
    ),
    table=dict(
        fname="output.tab",
        output=["hsign", "tps"],
    ),
)

config = SwanConfig(
    cgrid=cgrid,
    output=output,
    ...
)
```

## LockupInterface

The `LockupInterface` configures compute commands based on the simulation period.

### Basic Usage

```python
from rompy_swan.interface import LockupInterface

lockup = LockupInterface(
    compute=dict(model_type="nonstat"),
)

config = SwanConfig(
    cgrid=cgrid,
    lockup=lockup,
    ...
)
```

## SwanDataGrid

The `SwanDataGrid` class handles data loading and interpolation for input grids.

```python
from rompy_swan.data import SwanDataGrid

data = SwanDataGrid(
    source=dict(uri="bathymetry.nc"),
    var="elevation",
    coords=dict(x="longitude", y="latitude"),
)

# Get data for a specific grid and time
ds = data.get(destdir="/path/to/run", grid=grid, time=time_range)
```

### Variable Mapping

Map source variable names to SWAN conventions:

```python
data = SwanDataGrid(
    source=dict(uri="wind.nc"),
    var=["u10", "v10"],  # Source variable names
    coords=dict(
        x="longitude",
        y="latitude",
        time="time",
    ),
)
```

### Interpolation

Data is automatically interpolated to the SWAN grid:

```python
data = SwanDataGrid(
    source=dict(uri="bathymetry.nc"),
    var="elevation",
    interpolator=dict(
        model_type="regular_grid",
        method="linear",
    ),
)
```

## YAML Configuration

Data interfaces can be configured in YAML:

```yaml
inpgrid:
  model_type: data_interface
  bottom:
    model_type: swan_data_grid
    source:
      uri: bathymetry.nc
    var: elevation
  wind:
    model_type: swan_data_grid
    source:
      uri: wind.nc
    var:
      - u10
      - v10

boundary:
  model_type: boundary_interface
  source:
    uri: spectra.nc
  location:
    model_type: side
    side: west
```

## Next Steps

- [DataInterface](data.md) — Detailed data interface reference
- [BoundaryInterface](boundary.md) — Boundary condition interface
- [Grid](grid.md) — SWAN grid configuration
- [Sources](sources.md) — Data source types
