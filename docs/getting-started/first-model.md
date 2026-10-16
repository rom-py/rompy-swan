# Your first model

This page builds a small stationary SWAN model of swell arriving off south-western Australia, writes its workspace and shows how to run it. Every step on this page is executed when the docs are built, so the output shown is what the code produces. The model uses the coarse test data in the repository's `tests/data` folder. [Tutorial lesson 1](https://rom-py.github.io/rompy-notebooks/notebooks/swan/tutorial/01_first_model/) builds a similar model at higher resolution off Perth, as a notebook with plots of the results.

```python exec="on" session="first"
# Hidden setup: quiet logging and a temporary output folder.
import tempfile

from rompy.logging import config as logging_config

logging_config.update(level="WARNING")
OUT_DIR = tempfile.mkdtemp()
```

## 1. Run period

[`TimeRange`][rompy.core.time.TimeRange] comes from rompy and defines when the model runs. This first model is stationary: SWAN computes the wave field for a single moment, so the start and end are the same.

```python exec="on" source="above" session="first"
from rompy.core.time import TimeRange

period = TimeRange(start="2023-01-01T00:00", end="2023-01-01T00:00", interval="1h")
```

## 2. Computational grid

A [`SwanGrid`][rompy_swan.grid.SwanGrid] describes a regular grid by its lower-left corner, spacing and number of points, here in longitude and latitude. The computational grid component, [`REGULAR`][rompy_swan.components.cgrid.REGULAR], adds the spectral grid: 36 directions and frequencies from 0.04 to 1 Hz. It renders the SWAN `CGRID` command:

```python exec="on" source="above" result="text" session="first"
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.grid import SwanGrid
from rompy_swan.subcomponents.spectrum import SPECTRUM

grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)
cgrid = REGULAR(grid=grid.component, spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0))
print(cgrid.render())
```

## 3. Bathymetry

A [`SwanDataGrid`][rompy_swan.data.SwanDataGrid] turns a dataset into a SWAN input grid. Here it reads the elevation from a GEBCO file. SWAN expects depths positive down, so `fac=-1` flips the sign, and the data is cropped to the grid with a buffer. The [`DataInterface`][rompy_swan.interface.DataInterface] writes the input grid files and their `INPGRID` and `READINP` commands when the workspace is generated.

```python exec="on" source="above" session="first"
from rompy.core.source import SourceFile
from rompy_swan.data import SwanDataGrid
from rompy_swan.interface import DataInterface

bottom = SwanDataGrid(
    var="bottom",
    source=SourceFile(uri="tests/data/gebco-1deg.nc"),
    z1="elevation",
    fac=-1.0,
    coords={"x": "lon", "y": "lat"},
    buffer=1.0,
)
inpgrid = DataInterface(bottom=bottom)
```

## 4. Wave boundary

Swell enters through the western side of the grid. [`BOUNDSPEC`][rompy_swan.components.boundary.BOUNDSPEC] applies a JONSWAP spectrum with a significant wave height of 2 m, a peak period of 12 s, waves coming from 240° and a directional spreading of 20°:

```python exec="on" source="above" result="text" session="first"
from rompy_swan.components.boundary import BOUNDSPEC
from rompy_swan.subcomponents.boundary import CONSTANTPAR, SIDE
from rompy_swan.subcomponents.spectrum import JONSWAP, SHAPESPEC

boundary = BOUNDSPEC(
    shapespec=SHAPESPEC(shape=JONSWAP(gamma=3.3), per_type="peak", dspr_type="degrees"),
    location=SIDE(side="west", direction="ccw"),
    data=CONSTANTPAR(hs=2.0, per=12.0, dir=240.0, dd=20.0),
)
print(boundary.render())
```

## 5. Startup, physics, output and computation

- **Startup:** `SET NAUTICAL` makes directions mean *coming from*, clockwise from north, and the coordinates are spherical.
- **Physics:** `GEN3` is SWAN's third-generation physics. There is no wind in this model, so the quadruplet interactions are switched off, as SWAN requires.
- **Output:** a `BLOCK` writes maps on the computational grid (`COMPGRID`) to a NetCDF file.
- **Lockup:** `COMPUTE` runs the single computation of stationary mode, SWAN's default.

Commands that SWAN groups together are given as a group, such as [`STARTUP`][rompy_swan.components.group.STARTUP] or [`PHYSICS`][rompy_swan.components.group.PHYSICS]:

```python exec="on" source="above" session="first"
from rompy_swan.components.group import LOCKUP, OUTPUT, PHYSICS, STARTUP
from rompy_swan.components.lockup import COMPUTE
from rompy_swan.components.output import BLOCK
from rompy_swan.components.physics import GEN3, OFF, OFFS
from rompy_swan.components.startup import COORDINATES, PROJECT, SET
from rompy_swan.subcomponents.startup import SPHERICAL

startup = STARTUP(
    project=PROJECT(name="First model", nr="t01"),
    set=SET(direction_convention="nautical"),
    coordinates=COORDINATES(kind=SPHERICAL()),
)
physics = PHYSICS(gen=GEN3(), deactivate=OFFS(offs=[OFF(physics="quadrupl")]))
output = OUTPUT(
    block=BLOCK(sname="COMPGRID", fname="swangrid.nc", output=["depth", "hsign", "dir", "tps"])
)
lockup = LOCKUP(compute=COMPUTE())
```

## 6. The model configuration

[`SwanConfig`][rompy_swan.config.SwanConfig] gathers the pieces. Only `cgrid` is required; everything else is added as needed.

```python exec="on" source="above" session="first"
from rompy_swan.config import SwanConfig

config = SwanConfig(
    startup=startup,
    cgrid=cgrid,
    inpgrid=inpgrid,
    boundary=boundary,
    physics=physics,
    output=output,
    lockup=lockup,
)
```

## 7. Generate the workspace

rompy's [`ModelRun`][rompy.model.ModelRun] combines the configuration with the run period and an output directory. Calling it writes the workspace into `output_dir/run_id`: the bathymetry cropped to the grid (`bottom.grd`) and the command file `INPUT`.

```python exec="on" source="above" result="text" session="first"
from pathlib import Path

from rompy.model import ModelRun

modelrun = ModelRun(run_id="first_model", period=period, output_dir=OUT_DIR, config=config)
workspace = Path(modelrun())
print(sorted(p.name for p in workspace.iterdir()))
```

Each object above wrote its commands to `INPUT`, in the order SWAN expects (comment lines starting with `!` are left out here):

```python exec="on" source="above" result="text" session="first"
input_file = (workspace / "INPUT").read_text()
print("\n".join(line for line in input_file.splitlines() if line and line[0] != "!"))
```

## 8. Run SWAN

The easiest way to run SWAN is the public Docker image, through rompy's [`DockerConfig`][rompy.backends.config.DockerConfig] backend:

```python
from rompy.backends import DockerConfig

backend = DockerConfig(image="ghcr.io/rom-py/swan:41.51", executable="swan.exe")
modelrun.run(backend, workspace_dir=workspace)
```

SWAN writes a log of the run to `PRINT` and the maps to `swangrid.nc` in the workspace. With your own SWAN installation, run `swan.exe` from inside the workspace folder instead. [Running SWAN](../user-guide/running.md) covers backends, MPI and checking a run.

## Next steps

- The [tutorial](../tutorial.md) goes through each part of the model in turn, on a realistic model off Perth.
- [How rompy-swan works](../user-guide/how-it-works.md) explains how these objects become the command file.
- The [User guide](../user-guide/configuration.md) covers each part of the model in detail.
