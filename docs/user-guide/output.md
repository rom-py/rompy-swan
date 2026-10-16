# Output

SWAN writes output at named sets of locations: the computational grid, a frame, a sub-grid, points, curves or depth contours. Write commands then say what to write there and where: maps (`BLOCK`), tables (`TABLE`), spectra (`SPECOUT`) or boundary spectra for a nested model (`NESTOUT`). In rompy-swan each command is a component named after it, and the [`OUTPUT`][rompy_swan.components.group.OUTPUT] group, the `output` field of [`SwanConfig`][rompy_swan.config.SwanConfig], writes them in order and checks that every write command refers to locations that exist. This page covers the locations, the write commands, the output quantities and formats, the output times and how to read the files.

```python exec="on" session="output"
# Hidden setup: quiet logging and a temporary output folder.
import tempfile

from rompy.logging import config as logging_config

logging_config.update(level="WARNING")
OUT_DIR = tempfile.mkdtemp()
```

## The OUTPUT group

[`OUTPUT`][rompy_swan.components.group.OUTPUT] takes one component per field and writes them in this order, locations first:

| Field | Components | SWAN commands |
|---|---|---|
| `frame` | [`FRAME`][rompy_swan.components.output.FRAME] | `FRAME` |
| `group` | [`GROUP`][rompy_swan.components.output.GROUP] | `GROUP` |
| `curve` | [`CURVES`][rompy_swan.components.output.CURVES] | one `CURVE` per curve |
| `ray` | [`RAY`][rompy_swan.components.output.RAY] | `RAY` |
| `isoline` | [`ISOLINE`][rompy_swan.components.output.ISOLINE] | `ISOLINE` |
| `points` | [`POINTS`][rompy_swan.components.output.POINTS], [`POINTS_FILE`][rompy_swan.components.output.POINTS_FILE] | `POINTS` |
| `nests` | list of [`NEST`][rompy_swan.components.output.NEST] | `NGRID` and `NESTOUT` per nest |
| `quantity` | [`QUANTITIES`][rompy_swan.components.output.QUANTITIES] | one `QUANTITY` per entry |
| `output_options` | [`OUTPUT_OPTIONS`][rompy_swan.components.output.OUTPUT_OPTIONS] | `OUTPUT OPTIONS` |
| `block` | [`BLOCK`][rompy_swan.components.output.BLOCK], [`BLOCKS`][rompy_swan.components.output.BLOCKS] | one `BLOCK` per map file |
| `table` | [`TABLE`][rompy_swan.components.output.TABLE] | `TABLE` |
| `specout` | [`SPECOUT`][rompy_swan.components.output.SPECOUT] | `SPECOUT` |
| `test` | [`TEST`][rompy_swan.components.output.TEST] | `TEST` |

The `ngrid` and `nestout` fields are deprecated: use `nests`, described in [Nesting](nesting.md).

```python exec="on" source="above" result="text" session="output"
from rompy_swan.components.group import OUTPUT
from rompy_swan.components.output import BLOCK, POINTS, SPECOUT, TABLE

output = OUTPUT(
    points=POINTS(sname="sites", xp=[113.0, 114.5], yp=[-32.0, -34.0]),
    block=BLOCK(sname="COMPGRID", fname="swangrid.nc", output=["depth", "hsign", "tps", "dir"]),
    table=TABLE(sname="sites", fname="sites.txt", output=["hsign", "tps", "dir"]),
    specout=SPECOUT(sname="sites", fname="spectra.nc"),
)
print(output.render())
```

The group checks the rules of the SWAN manual:

- each set of locations has a unique `sname` of at most 8 characters, which is not one of the special names;
- the `sname` of each write command is defined by a location component, or is a special name;
- `BLOCK` writes on `COMPGRID`, `BOTTGRID`, a `FRAME` or a `GROUP` only;
- an `ISOLINE` needs the `RAY` it names.

```python exec="on" source="above" result="text" session="output"
from pydantic import ValidationError

try:
    OUTPUT(table=TABLE(sname="buoys", fname="buoys.txt", output=["hsign"]))
except ValidationError as err:
    print(err.errors()[0]["msg"])
```

## Output locations

| Locations | Component | Use |
|---|---|---|
| `COMPGRID`, `BOTTGRID` | none: special names | the computational grid, the bottom grid; for `BLOCK` only |
| a regular grid of its own | [`FRAME`][rompy_swan.components.output.FRAME] | maps of part of the domain at another resolution or orientation |
| part of the computational grid | [`GROUP`][rompy_swan.components.output.GROUP] | maps on a sub-grid by indices, without interpolation (not on unstructured grids) |
| points | [`POINTS`][rompy_swan.components.output.POINTS], [`POINTS_FILE`][rompy_swan.components.output.POINTS_FILE] | buoys, sites; `POINTS_FILE` reads the coordinates from a file |
| points along lines | [`CURVES`][rompy_swan.components.output.CURVES] of [`CURVE`][rompy_swan.components.output.CURVE] | transects |
| points along a depth contour | [`RAY`][rompy_swan.components.output.RAY] and [`ISOLINE`][rompy_swan.components.output.ISOLINE] | e.g. conditions along the 10 m contour |
| the boundary of a nested grid | [`NGRID`][rompy_swan.components.output.NGRID] in a [`NEST`][rompy_swan.components.output.NEST] | boundary spectra for a nested model |

Coordinates are in the units of the computational grid: degrees with spherical coordinates, metres with Cartesian ones. Outside the computational grid, or on dry points, SWAN writes the exception value.

```python exec="on" source="above" result="text" session="output"
from rompy_swan.components.output import CURVE, CURVES, FRAME, GROUP, ISOLINE, POINTS_FILE, RAY

frame = FRAME(sname="coast", grid=dict(xp=114.0, yp=-35.0, alp=0.0, xlen=2.0, ylen=3.0, mx=40, my=60))
group = GROUP(sname="west", ix1=0, iy1=0, ix2=4, iy2=14)
curves = CURVES(
    curves=[CURVE(sname="transect", xp1=111.0, yp1=-33.0, npts=[20], xp=[115.0], yp=[-33.0])]
)
ray = RAY(rname="rays", xp1=111.0, yp1=-35.0, xq1=116.0, yq1=-35.0, npts=[10], xp=[111.0], yp=[-30.0], xq=[116.0], yq=[-30.0])
isoline = ISOLINE(sname="dep50", rname="rays", dep=50.0)
for location in [frame, group, curves, ray, isoline, POINTS_FILE(sname="buoys", fname="buoys.txt")]:
    print(location.render())
```

A `CURVE` has corner points `xp1`, `yp1`, then `xp`, `yp`; [`npts`][rompy_swan.components.output.CURVE.npts] gives the number of segments between successive corners, so `npts=[20]` gives 21 points. `RAY` defines master rays from (`xp`, `yp`) to (`xq`, `yq`), subdivided by `npts`; `ISOLINE` takes the points where the rays cross the depth contour `dep`.

## What to write

| Component | Writes | Locations |
|---|---|---|
| [`BLOCK`][rompy_swan.components.output.BLOCK] | maps of the [`output`][rompy_swan.components.output.BLOCK.output] quantities | `COMPGRID`, `BOTTGRID`, `FRAME`, `GROUP` |
| [`BLOCKS`][rompy_swan.components.output.BLOCKS] | several `BLOCK` files, each with its own locations, quantities and times | as `BLOCK` |
| [`TABLE`][rompy_swan.components.output.TABLE] | one row per location and time, [`format`][rompy_swan.components.output.TABLE.format] `"header"` (SWAN default), `"noheader"` or `"indexed"` | points, curves, frames, groups |
| [`SPECOUT`][rompy_swan.components.output.SPECOUT] | spectra, 2D ([`SPEC2D`][rompy_swan.subcomponents.output.SPEC2D], default) or 1D ([`SPEC1D`][rompy_swan.subcomponents.output.SPEC1D]), in absolute ([`ABS`][rompy_swan.subcomponents.output.ABS], default) or relative ([`REL`][rompy_swan.subcomponents.output.REL]) frequency | as `TABLE` |
| [`NESTOUT`][rompy_swan.components.output.NESTOUT] | 2D spectra along the boundary of a nested grid | `NGRID`, through `NEST` |
| [`TEST`][rompy_swan.components.output.TEST] | integral parameters and source terms at up to 50 points, for debugging | its own points |

The output quantities are SWAN's keywords in lower case: `hsign`, `hswell`, `dir`, `pdir`, `tps`, `tm01`, `tm02`, `dspr`, `depth`, `watlev`, `wind`, `vel`, `setup`, `qb`, `ubot`, `dissip`, `time`, `xp`, `yp` and many others, listed in [`BlockOptions`][rompy_swan.types.BlockOptions].

```python exec="on" source="above" result="text" session="output"
from rompy_swan.components.output import BLOCKS
from rompy_swan.subcomponents.output import REL, SPEC1D

maps = BLOCKS(
    components=[
        BLOCK(sname="COMPGRID", fname="swangrid.nc", output=["hsign", "hswell", "dir"]),
        BLOCK(sname="coast", fname="coast.nc", output=["hsign", "tps", "setup"]),
    ]
)
print(maps.render())
print(TABLE(sname="sites", format="noheader", fname="sites.txt", output=["time", "hsign", "tps"]).render())
print(SPECOUT(sname="sites", dim=SPEC1D(), freq=REL(), fname="spec1d.nc").render())
```

### File formats

The extension of [`fname`][rompy_swan.components.output.BLOCK.fname] sets the format SWAN writes:

| Extension | Format |
|---|---|
| `.nc` | NetCDF, one variable per quantity |
| `.mat` | MATLAB binary, single precision |
| anything else | text |

NetCDF output needs a SWAN built with NetCDF. The `ghcr.io/rom-py/swan` Docker image has it; the official `delftwaves/swan` image does not, and writes files named `.nc` as text. For text maps, `BLOCK` also takes `header=False`, the layout [`idla`][rompy_swan.components.output.BLOCK.idla] (1, 3 or 4) and the scaling [`unit`][rompy_swan.components.output.BLOCK.unit]; [`OUTPUT_OPTIONS`][rompy_swan.components.output.OUTPUT_OPTIONS] sets the comment character, the width of table fields and the decimals of block and spectral output:

```python exec="on" source="above" result="text" session="output"
from rompy_swan.components.output import OUTPUT_OPTIONS

print(BLOCK(sname="COMPGRID", fname="hsign.txt", header=False, idla=3, output=["hsign"]).render())
print(OUTPUT_OPTIONS(comment="%", field=10, ndec_block=5, len=8, ndec_spec=6).render())
```

## Quantity options: QUANTITY

[`QUANTITY`][rompy_swan.components.output.QUANTITY] changes how quantities are computed or written; the `quantity` field takes several in a [`QUANTITIES`][rompy_swan.components.output.QUANTITIES] list. The most used options:

| Option | Effect | SWAN default |
|---|---|---|
| `fswell` | upper frequency of the swell, for `hswell` | 0.1 Hz |
| `fmin`, `fmax` | frequency range of the integral parameters | 0 to 1000 Hz |
| `excv` | exception value, written at dry points or outside the grid | |
| `hexp` | highest expected value, which sets the decimals in tables with header | |
| `power` | power of the mean period `per` and wave length `wlen` | 1 |
| `ref` | reference time of `tsec` | start of the computation |
| `short`, `long` | names in table and block headers | SWAN's names |
| `coord` | directions and vectors relative to the problem coordinates or to the `FRAME` | `problemcoord` |

```python exec="on" source="above" result="text" session="output"
from rompy_swan.components.output import QUANTITIES, QUANTITY

quantity = QUANTITIES(
    quantities=[
        QUANTITY(output=["hswell"], fswell=0.08),
        QUANTITY(output=["hsign", "tps", "dir"], excv=-9.0),
        QUANTITY(output=["tm01"], fmin=0.04, fmax=0.5),
    ]
)
print(quantity.render())
```

## Output times

In **stationary** mode SWAN makes a single computation, and the write commands have no times: SWAN writes once, at the end. `SwanConfig` rejects write components with `times` in this mode (see [Stationary and nonstationary runs](modes.md)).

In **nonstationary** mode each write command takes output times. rompy-swan sets them from the run period when the workspace is generated: output starts at the run start and is written at the run interval. The [`times`][rompy_swan.components.output.BLOCK.times] field, a [`TimeRangeOpen`][rompy_swan.subcomponents.time.TimeRangeOpen], overrides them: `delt` sets another interval, `tbeg` a later start (for example to leave out the spin-up), and `dfmt` and `tfmt` the format of the interval and time. The same applies to `NESTOUT` in `nests`.

```python exec="on" source="above" result="text" session="output"
from datetime import datetime, timedelta
from pathlib import Path

from rompy.core.time import TimeRange
from rompy.model import ModelRun
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.group import LOCKUP, STARTUP
from rompy_swan.components.lockup import COMPUTE_NONSTAT
from rompy_swan.components.startup import MODE
from rompy_swan.config import SwanConfig
from rompy_swan.grid import SwanGrid
from rompy_swan.subcomponents.spectrum import SPECTRUM
from rompy_swan.subcomponents.time import TimeRangeOpen

grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)
output = OUTPUT(
    points=POINTS(sname="sites", xp=[113.0, 114.5], yp=[-32.0, -34.0]),
    # Every run interval, from the run start
    block=BLOCK(sname="COMPGRID", fname="swangrid.nc", output=["hsign", "tps"]),
    # Every 3 hours
    table=TABLE(
        sname="sites",
        fname="sites.txt",
        output=["time", "hsign", "tps"],
        times=TimeRangeOpen(delt=timedelta(hours=3), dfmt="hr"),
    ),
    # Every hour, after a 6-hour spin-up
    specout=SPECOUT(
        sname="sites",
        fname="spectra.nc",
        times=TimeRangeOpen(tbeg=datetime(2023, 1, 1, 6), delt=timedelta(hours=1), dfmt="hr"),
    ),
)
config = SwanConfig(
    startup=STARTUP(mode=MODE(kind="nonstationary")),
    cgrid=REGULAR(grid=grid.component, spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0)),
    output=output,
    lockup=LOCKUP(compute=COMPUTE_NONSTAT()),
)
period = TimeRange(start="2023-01-01T00:00", end="2023-01-02T00:00", interval="30m")
workspace = Path(ModelRun(run_id="output", period=period, output_dir=OUT_DIR, config=config)())
input_file = (workspace / "INPUT").read_text()
section = input_file[input_file.index("! Output") :].splitlines()
print("\n".join(line for line in section if line and line[0] != "!"))
```

The `OUTPUT` keyword and the times follow the output quantities of each write command, and `COMPUTE NONSTATIONARY` takes the run period.

## Reading the output

SWAN writes the output files into the workspace. These examples need SWAN output, so they are not run here; the [output example](https://rom-py.github.io/rompy-notebooks/notebooks/swan/examples/output/) and [tutorial lesson 6](https://rom-py.github.io/rompy-notebooks/notebooks/swan/tutorial/06_nonstationary_hindcast/) run them on real results.

NetCDF maps open with xarray. SWAN uses short variable names, for example `hs` for `HSIGN`, `hswe` for `HSWELL` and `xwnd`, `ywnd` for `WIND`:

```python
import xarray as xr

maps = xr.open_dataset(workspace / "swangrid.nc")
maps.hs.sel(time="2023-01-01T12:00").plot()
```

A text table has one row per location and time, the locations repeating at each time; with `format="header"` the header lines start with `%`:

```python
import pandas as pd

table = pd.read_csv(
    workspace / "sites.txt", comment="%", sep=r"\s+", names=["time", "hs", "tps"], dtype={"time": str}
)
table["time"] = pd.to_datetime(table["time"], format="%Y%m%d.%H%M%S")
table["site"] = ["site1", "site2"] * (len(table) // 2)
```

[wavespectra](https://wavespectra.readthedocs.io/) reads SWAN spectra, NetCDF with `read_ncswan` and text with `read_swan`:

```python
import wavespectra

spectra = wavespectra.read_ncswan(workspace / "spectra.nc")
print(spectra.spec.hs())
spectra.isel(site=0, time=-1).spec.plot()
```

Also read `PRINT` after each run: SWAN reports there the errors and warnings that can leave output files empty or incomplete. See [Running SWAN](running.md).

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["outputs"]))
```
