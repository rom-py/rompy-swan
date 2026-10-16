# Stationary and nonstationary runs

SWAN separates two things: the **mode** says whether the model has a notion of time, and the **computation** says how SWAN computes the wave field. In stationary mode, SWAN's default, nothing has a time and SWAN computes one wave field. In nonstationary mode, inputs, boundaries and output have times, and each computation is either stationary (the equilibrium wave field for the conditions at one time) or nonstationary (waves evolving from one time step to the next). rompy-swan sets the mode with [`MODE`][rompy_swan.components.startup.MODE] in [`SwanConfig.startup`][rompy_swan.config.SwanConfig.startup], the computation in [`SwanConfig.lockup`][rompy_swan.config.SwanConfig.lockup], and takes the times from the run period. This page shows how to choose and what `SwanConfig` checks.

```python exec="on" session="modes"
# Hidden setup: quiet logging and a temporary output folder.
import tempfile
from pathlib import Path

from rompy.logging import config as logging_config

logging_config.update(level="WARNING")
OUT_DIR = Path(tempfile.mkdtemp())
```

## Mode and computation

| `MODE` | Computation in `lockup.compute` | SWAN commands | Inputs and boundaries |
|---|---|---|---|
| `STATIONARY` (default, no `startup.mode`) | [`COMPUTE`][rompy_swan.components.lockup.COMPUTE] | `COMPUTE` | Bottom, constant `WIND` and `ICE` ([`SwanConfig.forcing`][rompy_swan.config.SwanConfig.forcing]), `BOUNDSPEC` with parameters |
| `NONSTATIONARY` | [`COMPUTE_STAT`][rompy_swan.components.lockup.COMPUTE_STAT] | `COMPUTE STATIONARY [time]`, one or a series | Anything, including time-varying data and the boundary interface |
| `NONSTATIONARY` | [`COMPUTE_NONSTAT`][rompy_swan.components.lockup.COMPUTE_NONSTAT] | `COMPUTE NONSTATIONARY [tbegc] [deltc] [tendc]` | As above |

`MODE` also takes `dim`, `twodimensional` (default) or `onedimensional`, for SWAN's 1D mode:

```python exec="on" source="above" result="text" session="modes"
from rompy_swan.components.startup import MODE

print(MODE().render())
print(MODE(kind="nonstationary").render())
print(MODE(kind="stationary", dim="onedimensional").render())
```

`SwanConfig` does not check the restrictions of 1D mode, such as no `BOUNDNEST`, `NGRID`, `NESTOUT` or `BLOCK`; see the [SWAN manual](https://swanmodel.sourceforge.io/online_doc/swanuse/swanuse.html).

## Stationary mode

A stationary model needs no `startup.mode`, and its computation is `COMPUTE()`, the single computation without times. Output components are written without times. [Your first model](../getting-started/first-model.md) is a complete stationary model.

```python exec="on" source="above" result="text" session="modes"
from rompy_swan.components.group import LOCKUP
from rompy_swan.components.lockup import COMPUTE

print(LOCKUP(compute=COMPUTE()).render())
```

`COMPUTE` can write the final wave field to a hotfile ([Hotstart and chained runs](hotstart.md)).

## Nonstationary mode

Set `startup.mode=MODE(kind="nonstationary")` and use `COMPUTE_STAT` or `COMPUTE_NONSTAT`. When the workspace is generated, their times are set from the run period, a rompy [`TimeRange`][rompy.core.time.TimeRange]. [`LockupInterface`][rompy_swan.interface.LockupInterface] does this inside `SwanConfig`; calling it directly shows what each computation writes for a 12-hour period with a 3-hour interval:

```python exec="on" source="above" result="text" session="modes"
from rompy.core.time import TimeRange
from rompy_swan.components.lockup import COMPUTE_NONSTAT, COMPUTE_STAT
from rompy_swan.interface import LockupInterface
from rompy_swan.subcomponents.time import NONSTATIONARY

period = TimeRange(start="2023-01-01T00:00", end="2023-01-01T12:00", interval="3h")
options = {
    "one stationary computation": COMPUTE_STAT(),
    "a series of stationary computations": COMPUTE_STAT(times=NONSTATIONARY()),
    "a nonstationary computation": COMPUTE_NONSTAT(),
    "stationary start, then nonstationary": COMPUTE_NONSTAT(initstat=True),
}
for name, compute in options.items():
    lockup = LockupInterface(group=LOCKUP(compute=compute), period=period).group
    print(f"{name}:\n{lockup.render()}\n")
```

- `COMPUTE_STAT()` computes once, at the start of the period.
- `COMPUTE_STAT(times=NONSTATIONARY())` computes at every interval from start to end.
- `COMPUTE_NONSTAT()` runs from start to end with the interval as the time step.
- `initstat=True` first computes a stationary wave field at the start time, so the run does not start from calm seas or from SWAN's default initial state.

### Where the times come from

| Commands | `tbeg` | Interval | `tend` |
|---|---|---|---|
| `COMPUTE STATIONARY`, `COMPUTE NONSTATIONARY` | Run start | Run interval | Run end |
| `BLOCK`, `TABLE`, `SPECOUT`, `NESTOUT` output | Run start, unless set in `times` | Run interval, unless set in `times` | (SWAN writes until the end) |
| Data interface input grids and boundary files | Data cropped to the run period | The data's own time step | |

The run times always override the times of the computation; its `times` field only sets the format: `tfmt` (time format) and `dfmt` (unit of the time step):

```python exec="on" source="above" result="text" session="modes"
compute = COMPUTE_NONSTAT(times=NONSTATIONARY(dfmt="min"))
print(LockupInterface(group=LOCKUP(compute=compute), period=period).group.render())
```

Output components keep a `tbeg` or `delt` set in their `times` field, a [`TimeRangeOpen`][rompy_swan.subcomponents.time.TimeRangeOpen], for example to write maps less often than every time step, or to leave a spin-up period out of the output. The full command file of a nonstationary model with a wind input and hourly output:

```python exec="on" source="above" result="text" session="modes"
from rompy.core.filters import Filter
from rompy.core.source import SourceFile
from rompy.model import ModelRun
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.group import OUTPUT, STARTUP
from rompy_swan.components.output import BLOCK, POINTS, TABLE
from rompy_swan.components.startup import COORDINATES
from rompy_swan.config import SwanConfig
from rompy_swan.data import SwanDataGrid
from rompy_swan.grid import SwanGrid
from rompy_swan.interface import DataInterface
from rompy_swan.subcomponents.spectrum import SPECTRUM
from rompy_swan.subcomponents.startup import SPHERICAL
from rompy_swan.subcomponents.time import TimeRangeOpen

grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)
cgrid = REGULAR(grid=grid.component, spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0))
wind = SwanDataGrid(
    var="wind",
    source=SourceFile(uri="tests/data/era5-20230101.nc"),
    z1="u10",
    z2="v10",
    coords={"x": "longitude", "y": "latitude"},
    filter=Filter(sort={"coords": ["latitude"]}),
    buffer=5.0,
)
config = SwanConfig(
    startup=STARTUP(mode=MODE(kind="nonstationary"), coordinates=COORDINATES(kind=SPHERICAL())),
    cgrid=cgrid,
    inpgrid=DataInterface(input=[wind]),
    output=OUTPUT(
        points=POINTS(sname="site", xp=[112.0], yp=[-32.0]),
        block=BLOCK(
            sname="COMPGRID",
            fname="swangrid.nc",
            output=["hsign", "dir"],
            times=TimeRangeOpen(delt="PT1H"),
        ),
        table=TABLE(sname="site", fname="site.txt", output=["time", "hsign"]),
    ),
    lockup=LOCKUP(compute=COMPUTE_NONSTAT(initstat=True)),
)
period = TimeRange(start="2023-01-01T00:00", end="2023-01-01T12:00", interval="10m")
workspace = Path(ModelRun(run_id="nonstat", period=period, output_dir=OUT_DIR, config=config)())
lines = (workspace / "INPUT").read_text().splitlines()
print("\n".join(line for line in lines if line and line[0] != "!"))
```

The time step, `deltc`, is the run interval: the 10-minute interval here gives 600 s steps, and the table, without its own `times`, is written every step. The SWAN manual advises steps of at most 10 minutes for nonstationary computations.

## What `SwanConfig` rejects

SWAN rejects time information in stationary mode, and `COMPUTE` without times in nonstationary mode. [`SwanConfig`][rompy_swan.config.SwanConfig] checks this when it is created (`compute_consistent_with_mode`), so the mistake shows before SWAN runs:

```python exec="on" source="above" result="text" session="modes"
from pydantic import ValidationError
from rompy.core.source import SourceWavespectra
from rompy_swan.boundary import Boundnest1
from rompy_swan.interface import BoundaryInterface

nonstationary = STARTUP(mode=MODE(kind="nonstationary"))
spectra = BoundaryInterface(
    kind=Boundnest1(
        id="aus",
        source=SourceWavespectra(uri="tests/data/aus-20230101.nc", reader="read_wavespectra"),
    )
)
cases = {
    "COMPUTE_STAT in stationary mode": dict(lockup=LOCKUP(compute=COMPUTE_STAT())),
    "COMPUTE in nonstationary mode": dict(startup=nonstationary, lockup=LOCKUP(compute=COMPUTE())),
    "data inputs in stationary mode": dict(
        inpgrid=DataInterface(input=[wind]), boundary=spectra, lockup=LOCKUP(compute=COMPUTE())
    ),
    "output times in stationary mode": dict(
        output=OUTPUT(
            block=BLOCK(sname="COMPGRID", fname="a.nc", output=["hsign"], times=TimeRangeOpen())
        )
    ),
}
for name, kwargs in cases.items():
    try:
        SwanConfig(cgrid=cgrid, **kwargs)
    except ValidationError as err:
        print(f"{name}:\n  {err.errors()[0]['msg']}\n")
```

A bottom grid from the data interface is allowed in stationary mode: it has no times. All other input grids written by the data interface are time series, and need at least two times in the data within the run period, even for a field that does not change, such as friction. `BOUNDSPEC` with a TPAR file (`CONSTANTFILE`) is not checked; it also needs nonstationary mode.

## A stationary computation at a given time

To compute a stationary wave field for the conditions at one time, with wind, currents or boundary spectra from data, use nonstationary mode with a single `COMPUTE_STAT`. SWAN then reads the time series and computes at the given time. The run period must include at least two times of each data input, so let it end after the computation time; the computation is at its start:

```python exec="on" source="above" result="text" session="modes"
config = SwanConfig(
    startup=STARTUP(mode=MODE(kind="nonstationary"), coordinates=COORDINATES(kind=SPHERICAL())),
    cgrid=cgrid,
    inpgrid=DataInterface(input=[wind]),
    output=OUTPUT(block=BLOCK(sname="COMPGRID", fname="swangrid.nc", output=["hsign"])),
    lockup=LOCKUP(compute=COMPUTE_STAT()),
)
period = TimeRange(start="2023-01-01T06:00", end="2023-01-01T12:00", interval="6h")
workspace = Path(ModelRun(run_id="stat_at_time", period=period, output_dir=OUT_DIR, config=config)())
lines = (workspace / "INPUT").read_text().splitlines()
print("\n".join(line for line in lines if line.startswith(("MODE", "COORD", "INPGRID", "BLOCK", "  ", "COMPUTE"))))
```

With a period that starts and ends at the same time, the wind has only one time and the data interface stops with `Nonstationary WIND input needs at least two times`.

## Series of stationary computations or a nonstationary run?

- **A series of stationary computations** (`COMPUTE_STAT(times=NONSTATIONARY())`) puts the waves in equilibrium with the conditions at each time. It allows long intervals and suits small domains, which waves cross in less than the interval. The SWAN manual recommends stationary computations for domains smaller than about 100 km.
- **A nonstationary computation** (`COMPUTE_NONSTAT`) follows the growth and travel of the waves, which matters for larger domains and fast-changing winds. Keep the time step at 10 minutes or less, with a Courant number (grid cells crossed per step by the dominant waves) below 10, and start with `initstat=True` or a hotfile.

[Hotstart and chained runs](hotstart.md) shows how to split a long nonstationary run.

## See it in the notebooks

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["time", "execution"]))
```
