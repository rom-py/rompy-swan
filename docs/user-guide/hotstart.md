# Hotstart and chained runs

A hotfile holds the entire wave field of a SWAN run at one time. The next run can start from it instead of from SWAN's default initial state, so a long hindcast can be split into shorter runs, a forecast can continue from the previous cycle, and spin-up is not repeated. SWAN writes hotfiles with the `HOTFILE` command, right after a `COMPUTE`, and reads them with `INITIAL HOTSTART`. In rompy-swan the hotfile is part of the computation in [`SwanConfig.lockup`][rompy_swan.config.SwanConfig.lockup], and the hotstart is [`SwanConfig.initial`][rompy_swan.config.SwanConfig.initial].

```python exec="on" session="hotstart"
# Hidden setup: quiet logging and a temporary output folder.
import tempfile
from pathlib import Path

from rompy.logging import config as logging_config

logging_config.update(level="WARNING")
OUT_DIR = Path(tempfile.mkdtemp())
```

## Writing hotfiles

[`HOTFILE`][rompy_swan.components.lockup.HOTFILE] names the file and its format. The computation components take it in their `hotfile` field.

### In stationary mode

[`COMPUTE`][rompy_swan.components.lockup.COMPUTE] writes the wave field at the end of its single computation:

```python exec="on" source="above" result="text" session="hotstart"
from rompy_swan.components.group import LOCKUP
from rompy_swan.components.lockup import COMPUTE, HOTFILE

print(LOCKUP(compute=COMPUTE(hotfile=HOTFILE(fname="hotfile.swn"))).render())
```

### In nonstationary mode

[`COMPUTE_NONSTAT`][rompy_swan.components.lockup.COMPUTE_NONSTAT] and [`COMPUTE_STAT`][rompy_swan.components.lockup.COMPUTE_STAT] also take `hottimes`, the times to write a hotfile: indices of the computation times (`-1` is the last) or datetimes. rompy-swan splits the computation at those times, writes a `HOTFILE` after each part, and adds the time to the file name with the `suffix` template (`_%Y%m%dT%H%M%S` by default). The times come from the run period, as for every computation ([Stationary and nonstationary runs](modes.md)):

```python exec="on" source="above" result="text" session="hotstart"
from rompy.core.time import TimeRange
from rompy_swan.components.lockup import COMPUTE_NONSTAT
from rompy_swan.interface import LockupInterface

period = TimeRange(start="2023-01-01T00:00", end="2023-01-02T00:00", interval="10m")
compute = COMPUTE_NONSTAT(hotfile=HOTFILE(fname="hotfile.swn"), hottimes=["2023-01-01T12:00", "2023-01-02T00:00"])
print(LockupInterface(group=LOCKUP(compute=compute), period=period).group.render())
```

`hotfile` without `hottimes` writes nothing, and the reverse: both are needed, and rompy-swan logs a warning if only one is given.

### Formats

`format` is SWAN's choice of hotfile format:

| `format` | SWAN | File |
|---|---|---|
| `None` (default) or `free` | `FREE` (SWAN's default) | ASCII, the same format as `SPECOUT` 2D spectra; readable, but large and slow to read |
| `unformatted` | `UNFORMATTED` | Binary; smaller and faster. Transfers between computers only if they follow the same binary conventions (word size, endianness) |

```python exec="on" source="above" result="text" session="hotstart"
print(HOTFILE(fname="hotfile.bin", format="unformatted").render())
```

The file name, with the time suffix, is limited to 36 characters.

## Starting from a hotfile

[`INITIAL`][rompy_swan.components.boundary.INITIAL] with [`HOTSINGLE`][rompy_swan.subcomponents.boundary.HOTSINGLE] reads one hotfile; its `format` must match the file's:

```python exec="on" source="above" result="text" session="hotstart"
from rompy_swan.components.boundary import INITIAL
from rompy_swan.subcomponents.boundary import HOTSINGLE

print(INITIAL(kind=HOTSINGLE(fname="hotfile_20230101T120000.swn", format="free")).render())
```

If the hotfile comes from a nonstationary run, SWAN takes the time in the file as the initial time of the computation. In a stationary run it is used as the first guess. The computational and spectral grids must be identical to those of the run that wrote it.

## Chaining runs

A chain is a sequence of [`ModelRun`][rompy.model.ModelRun]s with consecutive periods. Each run writes a hotfile at its end, and the next one starts from it. The first run starts with a stationary computation (`initstat=True`); the next ones start from the hotfile instead:

```python exec="on" source="above" session="hotstart"
from rompy.core.source import SourceFile
from rompy.model import ModelRun
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.boundary import BOUNDSPEC
from rompy_swan.components.group import PHYSICS, STARTUP
from rompy_swan.components.physics import GEN3, OFF, OFFS
from rompy_swan.components.startup import COORDINATES, MODE
from rompy_swan.config import SwanConfig
from rompy_swan.data import SwanDataGrid
from rompy_swan.grid import SwanGrid
from rompy_swan.interface import DataInterface
from rompy_swan.subcomponents.boundary import CONSTANTPAR, SIDE
from rompy_swan.subcomponents.spectrum import SHAPESPEC, SPECTRUM
from rompy_swan.subcomponents.startup import SPHERICAL

grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)


def swan_config(compute: COMPUTE_NONSTAT, initial: INITIAL | None = None) -> SwanConfig:
    """A nonstationary model without wind, with the given computation and initial state."""
    return SwanConfig(
        startup=STARTUP(mode=MODE(kind="nonstationary"), coordinates=COORDINATES(kind=SPHERICAL())),
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
        boundary=BOUNDSPEC(
            shapespec=SHAPESPEC(dspr_type="degrees"),
            location=SIDE(side="west"),
            data=CONSTANTPAR(hs=2.0, per=12.0, dir=240.0, dd=20.0),
        ),
        initial=initial,
        physics=PHYSICS(gen=GEN3(), deactivate=OFFS(offs=[OFF(physics="quadrupl")])),
        lockup=LOCKUP(compute=compute),
    )
```

Each run writes a hotfile at its last time, `hottimes=[-1]`, and the second reads the first one's:

```python exec="on" source="above" result="text" session="hotstart"
first = ModelRun(
    run_id="first",
    period=TimeRange(start="2023-01-01T00:00", end="2023-01-01T12:00", interval="10m"),
    output_dir=OUT_DIR,
    config=swan_config(
        COMPUTE_NONSTAT(initstat=True, hotfile=HOTFILE(fname="hotfile.swn"), hottimes=[-1])
    ),
)
second = ModelRun(
    run_id="second",
    period=TimeRange(start="2023-01-01T12:00", end="2023-01-02T00:00", interval="10m"),
    output_dir=OUT_DIR,
    config=swan_config(
        COMPUTE_NONSTAT(hotfile=HOTFILE(fname="hotfile.swn"), hottimes=[-1]),
        initial=INITIAL(kind=HOTSINGLE(fname="hotfile_20230101T120000.swn")),
    ),
)
for run in [first, second]:
    workspace = Path(run())
    lines = (workspace / "INPUT").read_text().splitlines()
    print(f"{run.run_id}:")
    print("\n".join(line for line in lines if line.startswith(("INITIAL", "COMPUTE", "HOTFILE"))))
```

The hotfile is written when SWAN runs, so it is copied into the next workspace between runs:

```python
import shutil

from rompy.backends import DockerConfig

backend = DockerConfig(image="ghcr.io/rom-py/swan:41.51", executable="swan.exe")
first_ws, second_ws = Path(first.output_dir) / "first", Path(second.output_dir) / "second"
if first.run(backend, workspace_dir=first_ws):
    shutil.copy(first_ws / "hotfile_20230101T120000.swn", second_ws)
    second.run(backend, workspace_dir=second_ws)
```

Between chained runs, keep:

- the same computational and spectral grids;
- the start of each run at the time of the hotfile it reads;
- the same forcing, so the runs reproduce a single long run. A [notebook](https://rom-py.github.io/rompy-notebooks/notebooks/swan/examples/hotstart_and_chained_runs/) compares a chain of two runs with one run over the whole period: they agree to about a centimetre.

In a single run, the wave field already carries over from one `COMPUTE` to the next unless an `INITIAL` comes between them, so `hottimes` within a run only serve to save restart points.

## Hotfiles with MPI

A parallel MPI run writes one hotfile per process, with the process number appended: `hotfile.swn-001`, `hotfile.swn-002`, ... There are two ways to start from them:

- [`HOTMULTIPLE`][rompy_swan.subcomponents.boundary.HOTMULTIPLE] reads the set of files: give the name without the process number, as in the `HOTFILE` that wrote them. The new run must use the same number of processes.
- Concatenate them into one file with SWAN's `hcat` utility (see the SWAN Implementation Manual; the `ghcr.io/rom-py/swan` image does not include it) and read it with `HOTSINGLE`, with any number of processes or none.

```python exec="on" source="above" result="text" session="hotstart"
from rompy_swan.subcomponents.boundary import HOTMULTIPLE

print(INITIAL(kind=HOTMULTIPLE(fname="hotfile_20230101T120000.swn", format="free")).render())
```

[Running SWAN](running.md) covers MPI runs.

## See it in the notebooks

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["hotstart"]))
```
