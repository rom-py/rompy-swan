# Input grids and forcing

SWAN reads bathymetry, water levels, currents, wind, bottom friction and other fields on their own *input grids*, which it interpolates onto the computational grid. Each input grid is declared with an [`INPGRID`](https://swanmodel.sourceforge.io/online_doc/swanuse/swanuse.html) command and read from a file with `READINP`. rompy-swan writes them in two ways: from data sources, with a [`DataInterface`][rompy_swan.interface.DataInterface] that also writes the files, or from files you prepare yourself, with [`INPGRIDS`][rompy_swan.components.group.INPGRIDS]. Wind and ice that are the same everywhere go in the [`FORCING`][rompy_swan.components.group.FORCING] group. This page covers all three.

```python exec="on" session="inpgrid"
# Hidden setup: quiet logging and a temporary output folder.
import tempfile
from pathlib import Path

from rompy.logging import config as logging_config

logging_config.update(level="WARNING")
OUT_DIR = Path(tempfile.mkdtemp())
```

## Choosing how to give the inputs

| | [`DataInterface`][rompy_swan.interface.DataInterface] | [`INPGRIDS`][rompy_swan.components.group.INPGRIDS] | [`FORCING`][rompy_swan.components.group.FORCING] |
|---|---|---|---|
| Field of `SwanConfig` | `inpgrid` | `inpgrid` | `forcing` |
| Input | datasets read by rompy sources | files you provide | constant values |
| Writes the data files | yes, cropped to the grid and run period | no | no files needed |
| Computational grid | `REGULAR` only | any | any |
| SWAN commands | `INPGRID` and `READINP` | `INPGRID` and `READINP` | `WIND`, `ICE` |

`inpgrid` takes either a `DataInterface` or `INPGRIDS`, not both. `forcing` can be combined with either.

## Input grids from data

A [`SwanDataGrid`][rompy_swan.data.SwanDataGrid] turns a dataset into one SWAN input grid. It builds on rompy's [`DataGrid`][rompy.core.data.DataGrid], which reads the data and crops it; rompy-swan adds the SWAN settings:

| Field | Meaning |
|---|---|
| `var` | The SWAN input grid: `bottom`, `wind`, `current`, `wlevel`, ... ([below](#which-fields)) |
| `source` | Where the data comes from: a rompy source such as [`SourceFile`][rompy.core.source.SourceFile] (any file xarray opens), [`SourceIntake`][rompy.core.source.SourceIntake] (a dataset in an intake catalogue) or [`SourceDatamesh`][rompy.core.source.SourceDatamesh] |
| `z1`, `z2` | The variables in the dataset: `z1` for a scalar field, `z1` and `z2` for the x and y components of a vector field |
| `fac` | SWAN's multiplication factor, written in `READINP`: `fac=-1` turns elevations (positive up) into depths (positive down) |
| `coords` | The names of the x, y and time coordinates in the dataset; the default is `longitude`, `latitude` and `time` |
| `buffer` | Extra distance around the computational grid when the data is cropped, in the grid's units |
| `time_buffer` | Extra source time steps before and after the run period, e.g. `[1, 1]` |
| `filter` | A rompy [`Filter`][rompy.core.filters.Filter] applied when the data is opened: sort, subset, crop or rename |
| `crop_data` | Crop the data to the grid and the run period (default `True`) |

### Bathymetry

The bathymetry is the `bottom` input grid. This GEBCO file holds elevations in a variable `elevation`, with coordinates `lon` and `lat`. `get()` crops the data to the grid plus a 1° buffer, writes the data file and returns the commands:

```python exec="on" source="above" result="text" session="inpgrid"
from rompy.core.source import SourceFile
from rompy.core.time import TimeRange
from rompy_swan.data import SwanDataGrid
from rompy_swan.grid import SwanGrid

grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)
period = TimeRange(start="2023-01-01T00:00", end="2023-01-01T12:00", interval="1h")

bottom = SwanDataGrid(
    var="bottom",
    source=SourceFile(uri="tests/data/gebco-1deg.nc"),
    z1="elevation",
    fac=-1.0,
    coords={"x": "lon", "y": "lat"},
    buffer=1.0,
)
print(bottom.get(OUT_DIR, grid=grid, time=period))
```

`INPGRID BOTTOM REG` gives the origin, rotation, number of meshes and spacing of the input grid, taken from the cropped data, and `EXC` the exception value that marks missing data. The data is written as it is, with `fac=-1` in `READINP`, so the exception value is multiplied by `fac` as SWAN expects (`-99` becomes `99`). The file `bottom.grd` holds one row per latitude, from south to north (`idla=3`):

```python exec="on" source="above" result="text" session="inpgrid"
print("\n".join((OUT_DIR / "bottom.grd").read_text().splitlines()[:3]))
```

After `get()`, the cropped data is also available as an xarray dataset, in `bottom.ds`, for plotting or checking.

### Wind and other time-varying fields

Wind is a vector, so it needs two variables: `z1` and `z2` are the eastward and northward components. Two details of this ERA5 file matter:

- its latitudes run north to south, and the `filter` sorts them so the data can be cropped;
- its 5° grid is coarse compared with the model, so a 5° `buffer` makes sure the wind covers the whole domain (see [Covering the computational grid](#covering-the-computational-grid)).

```python exec="on" source="above" result="text" session="inpgrid"
wind = SwanDataGrid(
    var="wind",
    source=SourceFile(uri="tests/data/era5-20230101.nc"),
    z1="u10",
    z2="v10",
    coords={"x": "longitude", "y": "latitude"},
    filter={"sort": {"coords": ["latitude"]}},
    buffer=5.0,
)
print(wind.get(OUT_DIR, grid=grid, time=period))
```

Every input grid other than the bottom is written as a time series: `INPGRID` ends with `NONSTATION`, the first time and the interval between the data times, and the file holds, for each time, a line with the time followed by the `z1` rows and then the `z2` rows:

```python exec="on" source="above" result="text" session="inpgrid"
print("\n".join((OUT_DIR / "wind.grd").read_text().splitlines()[:10]))
```

The times are those of the data, cropped to the run period: here the 6-hourly ERA5 times from 00:00 to 12:00. When the run starts between two data times, the first data time after the start would be the first one written, so add the previous time with `time_buffer`:

```python exec="on" source="above" result="text" session="inpgrid"
late_start = TimeRange(start="2023-01-01T03:00", end="2023-01-01T15:00", interval="1h")
for time_buffer in ([0, 0], [1, 1]):
    data = wind.model_copy(update={"time_buffer": time_buffer}, deep=True)
    print(time_buffer, data.get(OUT_DIR, grid=grid, time=late_start).splitlines()[0])
```

!!! note "Time-varying inputs need nonstationary mode"
    SWAN accepts no time information in stationary mode, its default, so a `DataInterface` with any input besides the bottom needs `MODE NONSTATIONARY` in `startup`. `SwanConfig` checks this (see [below](#using-the-input-grids-in-a-model)). The computation can still be stationary: `COMPUTE_STAT` computes the wave field in equilibrium with the conditions at the start of the run period. [Stationary and nonstationary runs](modes.md) explains the modes.

### Which fields

`var` takes one of SWAN's input grids:

| `var` | Field | Variables |
|---|---|---|
| `bottom` | Bathymetry, depth positive down | `z1` (use `fac=-1` for elevations) |
| `wlevel` | Water level | `z1` |
| `current` | Current velocity | `z1`, `z2`: x and y components |
| `vx`, `vy` | One component of the current | `z1` |
| `wind` | Wind velocity at 10 m | `z1`, `z2`: x and y components |
| `wx`, `wy` | One component of the wind | `z1` |
| `friction` | Bottom friction coefficient, for `FRICTION` | `z1` |
| `nplants` | Vegetation density, for `VEGETATION` | `z1` |
| `turbvisc` | Turbulent viscosity, for `TURBULENCE` | `z1` |
| `mudlayer` | Mud layer thickness, for `MUD` | `z1` |
| `aice`, `hice` | Sea ice concentration and thickness, for `SICE` | `z1` |
| `hss`, `tss` | Sea-swell height and period, for `SURFBEAT` | `z1` |

In spherical coordinates, x and y are east and north, as in most datasets.

As noted above, every field except `bottom` is written as a time series, and its file needs at least two times. This also applies to fields that do not change, such as a friction map: the dataset needs a time coordinate and at least two times within the run period (for example the same field at the start and end of the run). A dataset without a time coordinate fails when the file is written. For a constant field, writing the input grid by hand ([below](#hand-written-input-grids)) is an alternative.

### Covering the computational grid

The data is cropped to the bounding box of the computational grid plus `buffer`, and only data points inside that box are kept. With data coarser than the model, the points inside may not reach the edges of the grid. Here the computational grid spans 110–116°E and 36–29°S, but without a large enough buffer the 5° wind keeps only the points at 110–115°E and 35–30°S:

```python exec="on" source="above" result="text" session="inpgrid"
print("grid:", [float(v) for v in grid.bbox()])
for buffer in (0.0, 2.0, 5.0):
    data = wind.model_copy(update={"buffer": buffer}, deep=True)
    print(f"buffer={buffer}:", data.get(OUT_DIR, grid=grid, time=period).splitlines()[0])
```

Make each input grid cover the whole computational grid, so that SWAN has the field everywhere: use a buffer of at least one data spacing. When the crop keeps fewer than two points along an axis, `get()` stops with an error that suggests a larger buffer.

### Using the input grids in a model

A [`DataInterface`][rompy_swan.interface.DataInterface] groups the input grids of a model: the `bottom` and a list of other `input` grids, each with a different `var`. In stationary mode, the default, only the bottom is accepted:

```python exec="on" source="above" result="text" session="inpgrid"
from pydantic import ValidationError
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.config import SwanConfig
from rompy_swan.interface import DataInterface
from rompy_swan.subcomponents.spectrum import SPECTRUM

cgrid = REGULAR(grid=grid.component, spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0))
inpgrid = DataInterface(bottom=bottom, input=[wind])
try:
    SwanConfig(cgrid=cgrid, inpgrid=inpgrid)
except ValidationError as err:
    print(err.errors()[0]["msg"])
```

With `MODE NONSTATIONARY`, the interface writes its files and commands when the workspace is generated:

```python exec="on" source="above" result="text" session="inpgrid"
from rompy.model import ModelRun
from rompy_swan.components.group import LOCKUP, PHYSICS, STARTUP
from rompy_swan.components.lockup import COMPUTE_NONSTAT
from rompy_swan.components.physics import GEN3
from rompy_swan.components.startup import COORDINATES, MODE, SET
from rompy_swan.subcomponents.startup import SPHERICAL

config = SwanConfig(
    startup=STARTUP(
        set=SET(direction_convention="nautical"),
        mode=MODE(kind="nonstationary"),
        coordinates=COORDINATES(kind=SPHERICAL()),
    ),
    cgrid=cgrid,
    inpgrid=inpgrid,
    physics=PHYSICS(gen=GEN3()),
    lockup=LOCKUP(compute=COMPUTE_NONSTAT()),
)
modelrun = ModelRun(run_id="wind_sea", period=period, output_dir=OUT_DIR, config=config)
workspace = Path(modelrun())
print(sorted(p.name for p in workspace.iterdir()))
input_file = (workspace / "INPUT").read_text()
print("\n".join(line for line in input_file.splitlines() if line.startswith(("INPGRID", "READINP"))))
```

The input grid files are named after `var` (`bottom.grd`, `wind.grd`, ...). The `DataInterface` uses the computational grid of the `SwanConfig` to crop the data and the period of the `ModelRun` to select the times, so the same configuration can be generated for another period without changes.

## Hand-written input grids

When you prepare the input files yourself, or use a curvilinear or unstructured computational grid, describe each file with an `inpgrid` component: [`REGULAR`][rompy_swan.components.inpgrid.REGULAR], [`CURVILINEAR`][rompy_swan.components.inpgrid.CURVILINEAR] or [`UNSTRUCTURED`][rompy_swan.components.inpgrid.UNSTRUCTURED], each with a [`READINP`][rompy_swan.subcomponents.readgrid.READINP] that says how to read the file. [`INPGRIDS`][rompy_swan.components.group.INPGRIDS] groups them. rompy-swan writes the commands but does not create, copy or check the files, which must be in the workspace when SWAN runs.

```python exec="on" source="above" result="text" session="inpgrid"
from rompy_swan.components.group import INPGRIDS
from rompy_swan.components.inpgrid import REGULAR as INPGRID_REGULAR
from rompy_swan.subcomponents.readgrid import READINP

inpgrids = INPGRIDS(
    inpgrids=[
        INPGRID_REGULAR(
            grid_type="bottom",
            xpinp=109.0,
            ypinp=-37.0,
            alpinp=0.0,
            mxinp=80,
            myinp=90,
            dxinp=0.1,
            dyinp=0.1,
            excval=-99.0,
            readinp=READINP(fname1="my_bathymetry.bot", fac=1.0, idla=3),
        ),
        INPGRID_REGULAR(
            grid_type="current",
            xpinp=109.0,
            ypinp=-37.0,
            alpinp=0.0,
            mxinp=16,
            myinp=18,
            dxinp=0.5,
            dyinp=0.5,
            readinp=READINP(fname1="currents.txt"),
            nonstationary={
                "tbeg": "2023-01-01T00:00",
                "tend": "2023-01-02T00:00",
                "delt": "PT1H",
                "dfmt": "hr",
            },
        ),
    ]
)
print(inpgrids.render())
```

`mxinp` and `myinp` count meshes, one less than the points in the file, as for the computational grid. A time-varying input grid takes `nonstationary` times, which SWAN accepts in nonstationary mode only; unlike the data interface, `SwanConfig` does not check this for hand-written grids. Each `grid_type` can appear once.

## Constant wind and ice

When the wind or the sea ice is the same over the whole domain, SWAN takes it as a single value with the [`WIND`][rompy_swan.components.inpgrid.WIND] and [`ICE`][rompy_swan.components.inpgrid.ICE] commands, with no input grid. They go in the [`FORCING`][rompy_swan.components.group.FORCING] group, the `forcing` field of `SwanConfig`, which takes at most one of each:

```python exec="on" source="above" result="text" session="inpgrid"
from rompy_swan.components.group import FORCING
from rompy_swan.components.inpgrid import ICE, WIND

forcing = FORCING(wind=WIND(vel=12.0, dir=225.0), ice=ICE(aice=0.2, hice=0.5))
print(forcing.render())
```

The wind direction follows the convention set by `SET` (in nautical convention, 225° is a wind *from* the south-west). Constant forcing has no times, so it works in stationary mode, and it can be combined with input grids from a data interface, for example GEBCO bathymetry with a constant wind:

```python exec="on" source="above" result="text" session="inpgrid"
from rompy_swan.components.lockup import COMPUTE

config = SwanConfig(
    startup=STARTUP(set=SET(direction_convention="nautical"), coordinates=COORDINATES(kind=SPHERICAL())),
    cgrid=cgrid,
    inpgrid=DataInterface(bottom=bottom),
    forcing=FORCING(wind=WIND(vel=12.0, dir=225.0)),
    physics=PHYSICS(gen=GEN3()),
    lockup=LOCKUP(compute=COMPUTE()),
)
modelrun = ModelRun(run_id="constant_wind", period=period, output_dir=OUT_DIR, config=config)
input_file = (Path(modelrun()) / "INPUT").read_text()
print("\n".join(line for line in input_file.splitlines() if line.startswith(("INPGRID", "READINP", "WIND"))))
```

`WIND` and `ICE` used to be given inside `INPGRIDS`. That still works, but is deprecated and emits a `DeprecationWarning`; it also cannot be combined with a `DataInterface`, since `inpgrid` takes only one of the two. Move them to `forcing`:

```python exec="on" source="above" result="text" session="inpgrid"
import warnings

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    INPGRIDS(inpgrids=[WIND(vel=12.0, dir=225.0)])
print(caught[0].message)
```

## See it in the notebooks

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["input-data", "bathymetry", "wind", "currents", "sources"]))
```
