# Boundary and initial conditions

SWAN only knows the waves that enter through the boundaries of its computational grid. On a boundary without wave information it assumes that no waves come in, and the missing energy shows as a shadow spreading into the domain from the corners. rompy-swan writes the SWAN boundary commands (`BOUNDSPEC`, `BOUNDNEST1`, `BOUNDNEST2`, `BOUNDNEST3`) as components, and builds boundaries from the spectra of a larger wave model with a [`BoundaryInterface`][rompy_swan.interface.BoundaryInterface], which writes the boundary files into the workspace. Either goes in [`SwanConfig.boundary`][rompy_swan.config.SwanConfig.boundary]. The initial wave field, `INITIAL`, goes in [`SwanConfig.initial`][rompy_swan.config.SwanConfig.initial]. This page helps you choose a boundary and shows what each one writes.

```python exec="on" session="boundaries"
# Hidden setup: quiet logging and a temporary output folder.
import tempfile
from pathlib import Path

from rompy.logging import config as logging_config

logging_config.update(level="WARNING")
destdir = Path(tempfile.mkdtemp())
```

## Choosing a boundary

| Data you have | Use | SWAN command |
|---|---|---|
| Nothing, just a sea state to test, or uniform waves far offshore | [`BOUNDSPEC`][rompy_swan.components.boundary.BOUNDSPEC] with [`CONSTANTPAR`][rompy_swan.subcomponents.boundary.CONSTANTPAR] | `BOUNDSPEC ... CONSTANT PAR` |
| Parameters that change along a side | `BOUNDSPEC` with [`VARIABLEPAR`][rompy_swan.subcomponents.boundary.VARIABLEPAR] | `BOUNDSPEC ... VARIABLE PAR` |
| A TPAR or spectral file you made yourself (buoy, other model) | `BOUNDSPEC` with [`CONSTANTFILE`][rompy_swan.subcomponents.boundary.CONSTANTFILE] or [`VARIABLEFILE`][rompy_swan.subcomponents.boundary.VARIABLEFILE] | `BOUNDSPEC ... CONSTANT FILE` |
| Spectra from a wave model, on every open side | [`Boundnest1`][rompy_swan.boundary.Boundnest1] in a `BoundaryInterface` | `BOUNDNEST1 NEST` |
| Spectra from a wave model, on one side | [`BoundspecSide`][rompy_swan.boundary.BoundspecSide] in a `BoundaryInterface` | `BOUNDSPEC SIDE ... CONSTANT FILE` |
| Spectra from a wave model, on some sides or along a line | [`BoundspecSegmentXY`][rompy_swan.boundary.BoundspecSegmentXY] in a `BoundaryInterface` | `BOUNDSPEC SEGMENT XY ... CONSTANT FILE` |
| A parent SWAN run | `NESTOUT` in the parent, [`BOUNDNEST1`][rompy_swan.components.boundary.BOUNDNEST1] in the child ([Nesting](nesting.md)) | `BOUNDNEST1 NEST` |
| WAM boundary files | [`BOUNDNEST2`][rompy_swan.components.boundary.BOUNDNEST2] | `BOUNDNEST2 WAMNEST` |
| WAVEWATCH III boundary files (`ww3_outp`) | [`BOUNDNEST3`][rompy_swan.components.boundary.BOUNDNEST3] | `BOUNDNEST3 WW3` |

`SwanConfig.boundary` takes one boundary. The components only write a command; any file they name must be in the workspace. The boundary interface reads the source data and writes the files itself, and needs `MODE NONSTATIONARY` because its files have times (see [below](#the-nonstationary-requirement)).

## Parametric boundaries: `BOUNDSPEC`

[`BOUNDSPEC`][rompy_swan.components.boundary.BOUNDSPEC] has three parts: the spectral shape (`shapespec`), where the boundary is (`location`) and the wave parameters (`data`). It renders SWAN's `BOUND SHAPESPEC` command followed by `BOUNDSPEC`:

```python exec="on" source="above" result="text" session="boundaries"
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

`dir` follows the convention of `SET`: with `SET NAUTICAL` it is the direction the waves come from, clockwise from north.

### Spectral shape

[`SHAPESPEC`][rompy_swan.subcomponents.spectrum.SHAPESPEC] sets how SWAN builds a spectrum from the parameters:

| Field | Options | Meaning |
|---|---|---|
| `shape` | [`JONSWAP`][rompy_swan.subcomponents.spectrum.JONSWAP]`(gamma)` (default, `gamma=3.3`), [`PM`][rompy_swan.subcomponents.spectrum.PM], [`GAUSS`][rompy_swan.subcomponents.spectrum.GAUSS]`(sigfr)`, [`TMA`][rompy_swan.subcomponents.spectrum.TMA]`(gamma, d)`, [`BIN`][rompy_swan.subcomponents.spectrum.BIN] | The frequency shape: JONSWAP, Pierson-Moskowitz (fully developed sea), Gaussian of width `sigfr` in Hz (narrow swell), JONSWAP in finite depth `d`, or all energy in one frequency bin |
| `per_type` | `peak` (default), `mean` | Whether `per` is the peak period or the mean period (`Tm01`) |
| `dspr_type` | `power` (default), `degrees` | Whether `dd` is the power `m` of cos<sup>m</sup>, or the directional standard deviation in degrees |

```python exec="on" source="above" result="text" session="boundaries"
from rompy_swan.subcomponents.spectrum import BIN, GAUSS, PM

for shape in [PM(), GAUSS(sigfr=0.01), BIN()]:
    print(SHAPESPEC(shape=shape, per_type="mean", dspr_type="power").render())
```

!!! warning "Spreading units"
    `SHAPESPEC` defaults to `dspr_type="power"`, as SWAN does, so `dd=20` means cos<sup>20</sup>, a narrow spread, not 20°. Set `dspr_type="degrees"` to give the spreading in degrees. The boundary interface classes default to degrees.

### Location

`location` is a whole side or a segment:

- [`SIDE`][rompy_swan.subcomponents.boundary.SIDE] is one side of a regular grid (`north`, `south`, `east`, `west`, or a corner such as `sw`). `direction` (`ccw` or `clockwise`) sets which way distances along the side are counted, which matters for `VARIABLEPAR` and `VARIABLEFILE`. Counter-clockwise, the western side runs from north to south.
- [`SEGMENT`][rompy_swan.subcomponents.boundary.SEGMENT] is a line through points given in problem coordinates ([`XY`][rompy_swan.subcomponents.base.XY]) or grid indices ([`IJ`][rompy_swan.subcomponents.base.IJ]). The points need not be grid points.

```python exec="on" source="above" result="text" session="boundaries"
from rompy_swan.subcomponents.base import XY
from rompy_swan.subcomponents.boundary import SEGMENT

swell = CONSTANTPAR(hs=2.0, per=12.0, dir=240.0, dd=20.0)
jonswap = SHAPESPEC(dspr_type="degrees")
segment = SEGMENT(points=XY(x=[110.0, 110.0], y=[-36.0, -33.0]))
print(BOUNDSPEC(shapespec=jonswap, location=segment, data=swell).render())
```

In a `SEGMENT IJ`, `-1` stands for the last index along that axis. SWAN stops reading the segment at a negative index, so `SwanConfig` replaces `-1` with `mxc` or `myc` of the computational grid. Here the segment runs along the northern, western and southern sides of the 13 × 15 point demo grid:

```python exec="on" source="above" result="text" session="boundaries"
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.config import SwanConfig
from rompy_swan.grid import SwanGrid
from rompy_swan.subcomponents.base import IJ
from rompy_swan.subcomponents.spectrum import SPECTRUM

grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)
cgrid = REGULAR(grid=grid.component, spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0))

config = SwanConfig(
    cgrid=cgrid,
    boundary=BOUNDSPEC(
        shapespec=jonswap,
        location=SEGMENT(points=IJ(i=[-1, 0, 0, -1], j=[-1, -1, 0, 0])),
        data=swell,
    ),
)
print(config.boundary.render())
```

### Data

| `data` | SWAN | Use |
|---|---|---|
| [`CONSTANTPAR`][rompy_swan.subcomponents.boundary.CONSTANTPAR] | `CONSTANT PAR` | The same `hs`, `per`, `dir`, `dd` along the boundary |
| [`VARIABLEPAR`][rompy_swan.subcomponents.boundary.VARIABLEPAR] | `VARIABLE PAR` | Values at distances `len` along the side or segment; SWAN interpolates between them |
| [`CONSTANTFILE`][rompy_swan.subcomponents.boundary.CONSTANTFILE] | `CONSTANT FILE` | One file for the whole boundary: a TPAR file, or a SWAN 1D or 2D spectral file (`seq` picks the location in a multi-point file) |
| [`VARIABLEFILE`][rompy_swan.subcomponents.boundary.VARIABLEFILE] | `VARIABLE FILE` | Files at distances `len` along the side or segment |

`len` is a distance in metres, or degrees with spherical coordinates, from the first point of the side or segment in its counting direction. Here the waves grow northwards along the western side, which is 7° long and counted from south to north (`clockwise`):

```python exec="on" source="above" result="text" session="boundaries"
from rompy_swan.subcomponents.boundary import VARIABLEPAR

variable = VARIABLEPAR(
    hs=[1.5, 2.0, 2.5],
    per=[11.0, 12.0, 12.0],
    dir=[235.0, 240.0, 245.0],
    dd=[20.0, 20.0, 20.0],
    len=[0.0, 3.5, 7.0],
)
side = SIDE(side="west", direction="clockwise")
print(BOUNDSPEC(shapespec=jonswap, location=side, data=variable).render())
```

The doubled `& &` at the line ends is how rompy-swan currently writes these continuation lines; SWAN 41.51 reads them correctly.

A TPAR file is a time series of `hs`, `per`, `dir` and `dd` at one location, for example from a buoy. [`write_tpar`][rompy_swan.boundary.write_tpar] writes one from a pandas DataFrame indexed by time, with the columns in that order:

```python exec="on" source="above" result="text" session="boundaries"
import numpy as np
import pandas as pd
from rompy_swan.boundary import write_tpar
from rompy_swan.subcomponents.boundary import CONSTANTFILE

times = pd.date_range("2023-01-01", periods=4, freq="6h")
buoy = pd.DataFrame(
    {"hs": np.linspace(2.0, 3.0, 4), "tp": 12.0, "dir": 240.0, "dspr": 20.0}, index=times
)
write_tpar(buoy, destdir / "buoy.tpar")
print((destdir / "buoy.tpar").read_text())

tpar = BOUNDSPEC(shapespec=jonswap, location=SIDE(side="west"), data=CONSTANTFILE(fname="buoy.tpar", seq=1))
print(tpar.render())
```

A TPAR file has times, so it needs `MODE NONSTATIONARY`. File names are limited to 36 characters, and rompy-swan does not copy the file: put it in the workspace before running SWAN.

## Boundaries from wave model spectra

The boundary interface builds boundaries from 2D spectra at output sites of a larger wave model, such as WAVEWATCH III. Its `kind` is one of three classes, which share the selection options of rompy's [`BoundaryWaveStation`][rompy.core.boundary.BoundaryWaveStation]:

- `source`: a source returning a [wavespectra](https://wavespectra.readthedocs.io/) dataset, such as [`SourceWavespectra`][rompy.core.source.SourceWavespectra] with a wavespectra reader;
- `sel_method`: `idw` (default) interpolates between the sites within `sel_method_kwargs["tolerance"]`, weighting by inverse distance; `nearest` takes the closest site within the tolerance;
- `spacing`: the distance between boundary points, in the units of the grid coordinates; `"parent"` uses the spacing of the source sites, and by default every grid point on the boundary is used;
- `crop_data` and `buffer`: crop the source to the run period and to the grid with a buffer (2° by default) before selecting.

The examples use `aus-20230101.nc`, 6-hourly spectra at 412 sites around Australia, and a 12-hour run period:

```python exec="on" source="above" session="boundaries"
from rompy.core.source import SourceWavespectra
from rompy.core.time import TimeRange

period = TimeRange(start="2023-01-01T00:00", end="2023-01-01T12:00", interval="6h")
source = SourceWavespectra(uri="tests/data/aus-20230101.nc", reader="read_wavespectra")
selection = {"sel_method": "nearest", "sel_method_kwargs": {"tolerance": 3.0}}
```

The sites in this file are up to 3° apart, so the tolerance is large; with a real model output use a tolerance of one or two site spacings.

### Every open side: `Boundnest1`

[`Boundnest1`][rompy_swan.boundary.Boundnest1] selects spectra at points around the whole grid, writes them to one SWAN spectral file named after its `id` and returns the `BOUNDNEST1` command. `rectangle` is `closed` (default) or `open`. Its `get` method is what the boundary interface calls when the workspace is generated:

```python exec="on" source="above" result="text" session="boundaries"
from rompy_swan.boundary import Boundnest1

nest = Boundnest1(id="aus", source=source, spacing=1.0, **selection)
filename, cmd = nest.get(destdir, grid=grid, time=period)
print(cmd, "\n")
print("\n".join(filename.read_text().splitlines()[:12]))
```

The file lists the boundary points counter-clockwise from the south-western corner, then the frequencies, directions and spectra at each time. It can be read back with `wavespectra.read_swan` to check the boundary against its source before running SWAN.

### One side: `BoundspecSide`

[`BoundspecSide`][rompy_swan.boundary.BoundspecSide] takes the spectrum at the middle of one side and writes a `BOUNDSPEC SIDE` command with a file. `file_type="tpar"` (default) writes the integrated parameters (significant wave height, peak or mean period, peak direction and spreading in degrees); `"spec2d"` writes the full spectrum:

```python exec="on" source="above" result="text" session="boundaries"
from rompy_swan.boundary import BoundspecSide

west = BoundspecSide(id="west", source=source, location=SIDE(side="west"), **selection)
filename, cmd = west.get(destdir, grid=grid, time=period)
print(cmd, "\n")
print(filename.name)
print(filename.read_text())
```

With TPAR files SWAN rebuilds the spectrum from the parameters with the shape of `shapespec` (JONSWAP by default; `per_type` picks `tp` or `tm01`). Use `spec2d` when the shape matters, for example with swell and wind sea from different directions.

### Several sides or a line: `BoundspecSegmentXY`

[`BoundspecSegmentXY`][rompy_swan.boundary.BoundspecSegmentXY] splits the boundary into segments between consecutive points and writes one boundary per segment, from the average of the spectra at its two ends. The points come from one side ([`SIDE`][rompy_swan.subcomponents.boundary.SIDE]), several contiguous sides ([`SIDES`][rompy_swan.subcomponents.boundary.SIDES]) or coordinates ([`XY`][rompy_swan.subcomponents.base.XY]). Here the southern and western sides, clockwise, every 2°, leaving the eastern side (the coast) without a boundary:

```python exec="on" source="above" result="text" session="boundaries"
from rompy_swan.boundary import BoundspecSegmentXY
from rompy_swan.subcomponents.boundary import SIDES

segments = BoundspecSegmentXY(
    id="sw",
    source=source,
    location=SIDES(
        sides=[SIDE(side="south", direction="clockwise"), SIDE(side="west", direction="clockwise")]
    ),
    spacing=2.0,
    **selection,
)
filenames, cmd = segments.get(destdir, grid=grid, time=period)
print(cmd)
```

The sides in `SIDES` must follow each other in the direction given.

### Files written

| Class | Files | Command |
|---|---|---|
| `Boundnest1` | `{id}.bnd`: SWAN 2D spectra at all boundary points | `BOUNDNEST1 NEST '{id}.bnd' CLOSED` |
| `BoundspecSide` | `{id}_{file_type}_{side}_000.bnd`: TPAR or 2D spectra | `BOUND SHAPESPEC` and one `BOUNDSPEC SIDE` |
| `BoundspecSegmentXY` | `{id}_{file_type}_000.bnd`, `_001`, ...: one per segment | `BOUND SHAPESPEC` and one `BOUNDSPEC SEGMENT XY` per segment |

When a boundary point is beyond the tolerance of every site, or outside the source, rompy-swan stops with an error instead of writing incomplete files:

```python exec="on" source="above" result="text" session="boundaries"
try:
    Boundnest1(id="short", source=source, sel_method="idw", sel_method_kwargs={"tolerance": 0.5}).get(
        destdir, grid=grid, time=period
    )
except ValueError as err:
    print(err)
```

Points on land still need a spectrum in the file, although SWAN ignores them.

Some options of `BoundspecSide` and `BoundspecSegmentXY` are not implemented: `variable=True` (spectra varying along a side) and `dspr_type="power"` in the TPAR files raise `NotImplementedError`, and their sides are taken from a regular grid without rotation.

### The nonstationary requirement

The interface's files have times, so the model needs `MODE NONSTATIONARY` and a computation at given times. In stationary mode, SWAN's default, `SwanConfig` rejects it:

```python exec="on" source="above" result="text" session="boundaries"
from pydantic import ValidationError
from rompy_swan.interface import BoundaryInterface

try:
    SwanConfig(cgrid=cgrid, boundary=BoundaryInterface(kind=nest))
except ValidationError as err:
    print(err.errors()[0]["msg"])
```

With `MODE NONSTATIONARY`, the interface writes its files into the workspace when [`ModelRun`][rompy.model.ModelRun] generates it, cropped to the run period:

```python exec="on" source="above" result="text" session="boundaries"
from rompy.model import ModelRun
from rompy_swan.components.group import LOCKUP, STARTUP
from rompy_swan.components.lockup import COMPUTE_NONSTAT
from rompy_swan.components.startup import MODE

config = SwanConfig(
    startup=STARTUP(mode=MODE(kind="nonstationary")),
    cgrid=cgrid,
    boundary=BoundaryInterface(kind=Boundnest1(id="aus", source=source, spacing=1.0, **selection)),
    lockup=LOCKUP(compute=COMPUTE_NONSTAT()),
)
workspace = Path(ModelRun(run_id="spectra", period=period, output_dir=destdir, config=config)())
print(sorted(p.name for p in workspace.iterdir()))
lines = (workspace / "INPUT").read_text().splitlines()
print("\n".join(line for line in lines if line.startswith(("MODE", "BOUND", "COMPUTE"))))
```

To compute a single stationary wave field from these spectra, use `COMPUTE_STAT` in nonstationary mode ([Stationary and nonstationary runs](modes.md#a-stationary-computation-at-a-given-time)).

### In YAML

The interface and its source are given by their `model_type`:

```python exec="on" source="above" result="text" session="boundaries"
import yaml

boundary_yaml = """
model_type: boundary_interface
kind:
  model_type: boundnest1
  id: aus
  source:
    model_type: wavespectra
    uri: tests/data/aus-20230101.nc
    reader: read_wavespectra
  sel_method: nearest
  sel_method_kwargs:
    tolerance: 3.0
  spacing: 1.0
"""
boundary = BoundaryInterface.model_validate(yaml.safe_load(boundary_yaml))
print(type(boundary.kind).__name__, boundary.kind.spacing)
```

## Boundaries from other models' files

`BOUNDNEST1`, `BOUNDNEST2` and `BOUNDNEST3` read boundary spectra written by a SWAN parent run (`NESTOUT`), WAM and WAVEWATCH III. SWAN interpolates them to its own frequencies, directions and boundary points. The components only name the file:

```python exec="on" source="above" result="text" session="boundaries"
from rompy_swan.components.boundary import BOUNDNEST1, BOUNDNEST2, BOUNDNEST3

print(BOUNDNEST1(fname="child.bnd", rectangle="closed").render())
print(BOUNDNEST2(fname="wamfiles.txt", format="free").render())
print(BOUNDNEST3(fname="ww3_boundary.out", format="unformatted").render())
```

For `BOUNDNEST2`, `fname` is a file listing the WAM files in time order. For `BOUNDNEST3`, the WAVEWATCH III files are written by `ww3_outp` at points along the SWAN boundary. None of them works in 1D mode. [Nesting](nesting.md) covers SWAN-in-SWAN nesting.

## Initial conditions: `INITIAL`

[`INITIAL`][rompy_swan.components.boundary.INITIAL] sets the wave field at the start of a nonstationary computation, replacing SWAN's default initialisation. In stationary mode SWAN only accepts `INITIAL HOTSTART`, as a first guess.

| `kind` | SWAN | Initial wave field |
|---|---|---|
| [`DEFAULT`][rompy_swan.subcomponents.boundary.DEFAULT] | `INITIAL DEFAULT` | From the local wind, with a deep-water growth curve |
| [`ZERO`][rompy_swan.subcomponents.boundary.ZERO] | `INITIAL ZERO` | No waves; with wind only, waves grow only through the `AGROW` term of `GEN3` |
| [`PAR`][rompy_swan.subcomponents.boundary.PAR] | `INITIAL PAR` | A spectrum from `hs`, `per`, `dir`, `dd`, with the shape of `BOUND SHAPESPEC` |
| [`HOTSINGLE`][rompy_swan.subcomponents.boundary.HOTSINGLE], [`HOTMULTIPLE`][rompy_swan.subcomponents.boundary.HOTMULTIPLE] | `INITIAL HOTSTART SINGLE/MULTIPLE` | Read from a hotfile of a previous run ([Hotstart and chained runs](hotstart.md)) |

```python exec="on" source="above" result="text" session="boundaries"
from rompy_swan.components.boundary import INITIAL
from rompy_swan.subcomponents.boundary import HOTSINGLE, PAR, ZERO

for kind in [ZERO(), PAR(hs=1.0, per=8.0, dir=240.0, dd=30.0), HOTSINGLE(fname="hotstart.swn")]:
    print(INITIAL(kind=kind).render())
```

An alternative to `INITIAL` for a nonstationary run is `COMPUTE_NONSTAT(initstat=True)`, which first makes a stationary computation at the start time ([Stationary and nonstationary runs](modes.md)).

## See it in the notebooks

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["boundary-conditions", "input-data"]))
```
