# Nesting

Nesting runs a coarse SWAN model over a large area (the parent) and uses its spectra as the boundary of a finer model near the coast (the child). The parent writes 2D spectra along the child's boundary with SWAN's `NGRID` and `NESTOUT` commands, and the child reads them with `BOUNDNEST1`. They are two separate SWAN runs: rompy-swan configures both, and you run the parent first and pass its boundary file to the child. This page shows the configuration on each side and how to chain the runs with rompy.

```python exec="on" session="nesting"
# Hidden setup: quiet logging and a temporary output folder.
import tempfile
from pathlib import Path

from rompy.logging import config as logging_config

logging_config.update(level="WARNING")
OUT_DIR = Path(tempfile.mkdtemp())
```

## The grids

The child grid must lie inside the parent grid, and both must use the same coordinate system (`COORDINATES`). Their spectral grids may differ: SWAN interpolates the parent's spectra to the child's frequencies and directions. Here a 0.5° parent covers south-western Australia and a 0.1° child a stretch of coast inside it:

```python exec="on" source="above" session="nesting"
from rompy_swan.grid import SwanGrid

parent_grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)
child_grid = SwanGrid(x0=113.0, y0=-34.0, dx=0.1, dy=0.1, nx=21, ny=31)
```

Both models in this page share everything but the grid, the boundary and the output: spherical coordinates, a GEBCO bathymetry, and a single stationary computation at the start of the run period, in nonstationary mode so the parent's boundary can come from wave model spectra ([Stationary and nonstationary runs](modes.md#a-stationary-computation-at-a-given-time)). There is no wind, so the quadruplets are switched off, as SWAN requires.

```python exec="on" source="above" session="nesting"
from rompy.core.source import SourceFile
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.group import LOCKUP, OUTPUT, PHYSICS, STARTUP
from rompy_swan.components.lockup import COMPUTE_STAT
from rompy_swan.components.physics import GEN3, OFF, OFFS
from rompy_swan.components.startup import COORDINATES, MODE, SET
from rompy_swan.config import SwanConfig
from rompy_swan.data import SwanDataGrid
from rompy_swan.interface import DataInterface
from rompy_swan.subcomponents.spectrum import SPECTRUM
from rompy_swan.subcomponents.startup import SPHERICAL


def swan_config(grid: SwanGrid, boundary, output: OUTPUT) -> SwanConfig:
    """A model on the given grid, with the given boundary and output."""
    return SwanConfig(
        startup=STARTUP(
            set=SET(direction_convention="nautical"),
            mode=MODE(kind="nonstationary"),
            coordinates=COORDINATES(kind=SPHERICAL()),
        ),
        cgrid=REGULAR(grid=grid.component, spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0)),
        inpgrid=DataInterface(
            bottom=SwanDataGrid(
                var="bottom",
                source=SourceFile(uri="tests/data/gebco-1deg.nc"),
                z1="elevation",
                fac=-1.0,
                coords={"x": "lon", "y": "lat"},
                buffer=1.0,
            )
        ),
        boundary=boundary,
        physics=PHYSICS(gen=GEN3(), deactivate=OFFS(offs=[OFF(physics="quadrupl")])),
        output=output,
        lockup=LOCKUP(compute=COMPUTE_STAT()),
    )
```

## The parent: `NGRID` and `NESTOUT`

In the parent's output, a [`NEST`][rompy_swan.components.output.NEST] pairs the child's boundary ([`NGRID`][rompy_swan.components.output.NGRID]) with the file the spectra are written to ([`NESTOUT`][rompy_swan.components.output.NESTOUT]), and gives both the same `sname`. [`OUTPUT.nests`][rompy_swan.components.group.OUTPUT.nests] takes a list, so one parent can feed several children; their `sname` must be unique. Building `NGRID` from the child's `SwanGrid` guarantees that it matches the child's `CGRID`:

```python exec="on" source="above" result="text" session="nesting"
from rompy.core.source import SourceWavespectra
from rompy_swan.boundary import Boundnest1
from rompy_swan.components.output import BLOCK, NEST, NESTOUT, NGRID
from rompy_swan.interface import BoundaryInterface

parent = swan_config(
    parent_grid,
    boundary=BoundaryInterface(
        kind=Boundnest1(
            id="aus",
            source=SourceWavespectra(uri="tests/data/aus-20230101.nc", reader="read_wavespectra"),
            sel_method="nearest",
            sel_method_kwargs={"tolerance": 3.0},
            spacing=1.0,
        )
    ),
    output=OUTPUT(
        block=BLOCK(sname="COMPGRID", fname="swangrid.nc", output=["hsign", "dir"]),
        nests=[
            NEST(
                sname="child",
                ngrid=NGRID(grid=child_grid.component),
                nestout=NESTOUT(fname="child.bnd"),
            )
        ],
    ),
)
print(parent.output.render())
```

`NESTOUT` is an output command: in nonstationary mode it is written at the start of the run and every run interval, unless its `times` field sets another `tbeg` or `delt` (see [Output](output.md)). Choose an interval that resolves the changes in the waves at the child's boundary. In stationary mode it has no times. For an unstructured child grid, use [`NGRID_UNSTRUCTURED`][rompy_swan.components.output.NGRID_UNSTRUCTURED].

!!! note "Deprecated `ngrid` and `nestout` fields"
    `OUTPUT` still accepts a single nest as its own `ngrid` and `nestout` fields, with the same `sname`. They are deprecated: `OUTPUT` converts them into one entry of `nests` and logs a warning. Giving both `nests` and `ngrid`/`nestout` is an error.

## The child: `BOUNDNEST1`

The child reads the parent's spectra with the [`BOUNDNEST1`][rompy_swan.components.boundary.BOUNDNEST1] component, which only names the file. `rectangle` is `closed` (default) for a boundary all around the grid, which is what `NESTOUT` writes.

```python exec="on" source="above" result="text" session="nesting"
from rompy_swan.components.boundary import BOUNDNEST1

child = swan_config(
    child_grid,
    boundary=BOUNDNEST1(fname="child.bnd", rectangle="closed"),
    output=OUTPUT(block=BLOCK(sname="COMPGRID", fname="swangrid.nc", output=["hsign", "dir"])),
)
print(child.boundary.render())
```

`BOUNDNEST1` is a component, not part of the boundary interface: it writes no file, so the child model can be in stationary mode when the parent is. A nonstationary child needs a nest file covering its computation times. `fname` is limited to 36 characters, and SWAN reads it relative to the child's workspace.

## Chaining the runs

Each model is a [`ModelRun`][rompy.model.ModelRun] with the same period. Both workspaces can be generated at once; the parent writes `child.bnd` when SWAN runs, so the file is copied into the child's workspace between the two runs:

```python exec="on" source="above" result="text" session="nesting"
from rompy.core.time import TimeRange
from rompy.model import ModelRun

period = TimeRange(start="2023-01-01T00:00", end="2023-01-01T12:00", interval="6h")
parent_run = ModelRun(run_id="parent", period=period, output_dir=OUT_DIR, config=parent)
child_run = ModelRun(run_id="child", period=period, output_dir=OUT_DIR, config=child)
parent_ws = Path(parent_run())
child_ws = Path(child_run())

for workspace in [parent_ws, child_ws]:
    lines = (workspace / "INPUT").read_text().splitlines()
    print(f"{workspace.name}:")
    print("\n".join(line for line in lines if line.startswith(("CGRID", "BOUND", "NGRID", "NESTOUT", "COMPUTE"))))
```

Then run them in order, here with Docker:

```python
import shutil

from rompy.backends import DockerConfig

backend = DockerConfig(image="ghcr.io/rom-py/swan:41.51", executable="swan.exe")
if parent_run.run(backend, workspace_dir=parent_ws):
    shutil.copy(parent_ws / "child.bnd", child_ws)
    child_run.run(backend, workspace_dir=child_ws)
```

Point `BOUNDNEST1` at a copy in the child's workspace rather than at a path into the parent's: a backend that mounts only the workspace, such as Docker, cannot see the parent's folder, and SWAN stops with `File cannot be opened/does not exist`. Check the child's `PRINT` and `Errfile` for such errors after the run ([Running SWAN](running.md)).

The parent's `child.bnd` is a standard SWAN spectral file with the points along the child's boundary. It can be read with `wavespectra.read_swan` to check it before running the child.

## Several levels and other parents

- A child can itself be a parent: give it `OUTPUT.nests` for the next grid and chain a third `ModelRun`.
- Spectra from other models enter the outermost grid with the boundary interface ([`Boundnest1`][rompy_swan.boundary.Boundnest1], from spectra at output sites) or with [`BOUNDNEST2`][rompy_swan.components.boundary.BOUNDNEST2] (WAM) and [`BOUNDNEST3`][rompy_swan.components.boundary.BOUNDNEST3] (WAVEWATCH III); see [Boundary and initial conditions](boundaries.md).
- For a curvilinear child grid the SWAN manual advises `POINTS` or `CURVE` with `SPECOUT` in the parent and `BOUNDSPEC` with a spectral file in the child, instead of `NGRID` and `NESTOUT`.

## See it in the notebooks

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["nesting", "boundary-conditions"]))
```
