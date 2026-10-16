# Configuration

A SWAN model is one [`SwanConfig`][rompy_swan.config.SwanConfig] object. It can be built in Python or written as YAML; both are validated by the same classes, so a YAML file is checked as thoroughly as Python code. This page lists what a `SwanConfig` holds, shows the same model in Python and YAML, and covers generating it with rompy's [`ModelRun`][rompy.model.ModelRun] and the `rompy` command line.

```python exec="on" session="configuration"
# Hidden setup: quiet logging and a temporary output folder.
import tempfile

from rompy.logging import config as logging_config

logging_config.update(level="WARNING")
OUT_DIR = tempfile.mkdtemp()
```

## What a `SwanConfig` holds

Each field is a section of the command file `INPUT`, and the sections are written in the order of this table, which is the order SWAN expects:

| Field | Takes | SWAN commands |
|---|---|---|
| `startup` | [`STARTUP`][rompy_swan.components.group.STARTUP] | `PROJECT`, `SET`, `MODE`, `COORDINATES` |
| `cgrid` (required) | [`REGULAR`][rompy_swan.components.cgrid.REGULAR], [`CURVILINEAR`][rompy_swan.components.cgrid.CURVILINEAR] or [`UNSTRUCTURED`][rompy_swan.components.cgrid.UNSTRUCTURED] | `CGRID`, and `READGRID` for curvilinear and unstructured grids |
| `inpgrid` | [`INPGRIDS`][rompy_swan.components.group.INPGRIDS] or a [`DataInterface`][rompy_swan.interface.DataInterface] | `INPGRID` and `READINP` |
| `forcing` | [`FORCING`][rompy_swan.components.group.FORCING] | constant `WIND` and `ICE` |
| `boundary` | [`BOUNDSPEC`][rompy_swan.components.boundary.BOUNDSPEC], [`BOUNDNEST1`][rompy_swan.components.boundary.BOUNDNEST1], `BOUNDNEST2`, `BOUNDNEST3` or a [`BoundaryInterface`][rompy_swan.interface.BoundaryInterface] | `BOUNDSPEC`, `BOUNDNEST1/2/3` |
| `initial` | [`INITIAL`][rompy_swan.components.boundary.INITIAL] | `INITIAL` |
| `physics` | [`PHYSICS`][rompy_swan.components.group.PHYSICS] | `GEN3`, `BREAKING`, `FRICTION`, `TRIAD`, `OFF`, ... |
| `prop` | [`PROP`][rompy_swan.components.numerics.PROP] | `PROP` |
| `numeric` | [`NUMERIC`][rompy_swan.components.numerics.NUMERIC] | `NUMERIC` |
| `output` | [`OUTPUT`][rompy_swan.components.group.OUTPUT] | locations, `QUANTITY`, `BLOCK`, `TABLE`, `SPECOUT`, `NESTOUT` |
| `lockup` | [`LOCKUP`][rompy_swan.components.group.LOCKUP] | `COMPUTE`, `HOTFILE`, `STOP` |

Only `cgrid` is required: it defines the grid that the interfaces use to crop data and place boundary points. A field left out writes nothing, and SWAN then uses its own defaults; without `lockup`, though, `INPUT` has no `COMPUTE` and SWAN computes nothing. `template` (from rompy's [`BaseConfig`][rompy.core.config.BaseConfig]) points to the command file template and rarely needs changing.

The run period is not part of the `SwanConfig`: it belongs to the `ModelRun`. In nonstationary mode it sets the times of the computation and the output (see [Stationary and nonstationary runs](modes.md)).

## Building a configuration in Python

Each field takes an object of the class listed above. The model below is the one from [Your first model](../getting-started/first-model.md): swell entering through the western side of a grid off south-western Australia, with GEBCO bathymetry.

```python exec="on" source="above" session="configuration"
from rompy.core.source import SourceFile
from rompy_swan.components.boundary import BOUNDSPEC
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.group import LOCKUP, OUTPUT, PHYSICS, STARTUP
from rompy_swan.components.lockup import COMPUTE
from rompy_swan.components.output import BLOCK
from rompy_swan.components.physics import GEN3, OFF, OFFS
from rompy_swan.components.startup import COORDINATES, PROJECT, SET
from rompy_swan.config import SwanConfig
from rompy_swan.data import SwanDataGrid
from rompy_swan.grid import SwanGrid
from rompy_swan.interface import DataInterface
from rompy_swan.subcomponents.boundary import CONSTANTPAR, SIDE
from rompy_swan.subcomponents.spectrum import JONSWAP, SHAPESPEC, SPECTRUM
from rompy_swan.subcomponents.startup import SPHERICAL

grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)

config = SwanConfig(
    startup=STARTUP(
        project=PROJECT(name="First model", nr="t01"),
        set=SET(direction_convention="nautical"),
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
        ),
    ),
    boundary=BOUNDSPEC(
        shapespec=SHAPESPEC(shape=JONSWAP(gamma=3.3), per_type="peak", dspr_type="degrees"),
        location=SIDE(side="west", direction="ccw"),
        data=CONSTANTPAR(hs=2.0, per=12.0, dir=240.0, dd=20.0),
    ),
    physics=PHYSICS(gen=GEN3(), deactivate=OFFS(offs=[OFF(physics="quadrupl")])),
    output=OUTPUT(
        block=BLOCK(sname="COMPGRID", fname="swangrid.nc", output=["depth", "hsign", "dir", "tps"])
    ),
    lockup=LOCKUP(compute=COMPUTE()),
)
```

Nested objects can also be given as dictionaries. Pydantic turns them into the right class, using `model_type` where a field accepts several classes (see [below](#choosing-between-classes-model_type)):

```python exec="on" source="above" result="text" session="configuration"
cgrid = {
    "model_type": "regular",
    "grid": {"xp": 110.0, "yp": -36.0, "xlen": 6.0, "ylen": 7.0, "mx": 12, "my": 14},
    "spectrum": {"mdc": 36, "flow": 0.04, "fhigh": 1.0},
}
print(SwanConfig(cgrid=cgrid).cgrid.render())
```

To make variants of a configuration, for a sensitivity test, copy it and replace a field. The original is unchanged:

```python exec="on" source="above" result="text" session="configuration"
from rompy_swan.components.physics import BREAKING_CONSTANT

physics = PHYSICS(
    gen=GEN3(),
    breaking=BREAKING_CONSTANT(alpha=1.0, gamma=0.6),
    deactivate=OFFS(offs=[OFF(physics="quadrupl")]),
)
variant = config.model_copy(update={"physics": physics})
print(variant.physics.render())
```

`model_copy` does not validate the new value, so a copy can hold a combination that `SwanConfig` would reject, such as a nonstationary computation in stationary mode. Build a new `SwanConfig` when the change touches settings that depend on each other.

## Generating the workspace

A [`ModelRun`][rompy.model.ModelRun] adds the run period ([`TimeRange`][rompy.core.time.TimeRange]), a run id and an output folder. Calling it writes the workspace into `output_dir/run_id`: the command file `INPUT` and the files written by the interfaces, here the bathymetry `bottom.grd`.

```python exec="on" source="above" result="text" session="configuration"
from pathlib import Path

from rompy.core.time import TimeRange
from rompy.model import ModelRun

modelrun = ModelRun(
    run_id="python_model",
    period=TimeRange(start="2023-01-01T00:00", end="2023-01-01T00:00", interval="1h"),
    output_dir=OUT_DIR,
    config=config,
)
workspace = Path(modelrun())
print(sorted(p.name for p in workspace.iterdir()))
```

The commands in `INPUT`, without the comment lines:

```python exec="on" source="above" result="text" session="configuration"
input_file = (workspace / "INPUT").read_text()
print("\n".join(line for line in input_file.splitlines() if line and line[0] != "!"))
```

[How rompy-swan works](how-it-works.md) describes the steps between the objects and `INPUT`.

## The same model as YAML

A YAML file holds the fields of a `ModelRun`: `run_id`, `output_dir`, `period` and `config`. Each nested object has the same fields as its Python class. The grid is given as the values of SWAN's `CGRID` command, which `grid.component` computed in Python (see [Computational grid](computational-grid.md)):

```python exec="on" result="yaml" session="configuration"
# Hidden: write the YAML file shown below into the temporary folder.
YAML_TEXT = """\
run_id: yaml_model
output_dir: output
delete_existing: true

period:
  start: 2023-01-01T00:00
  end: 2023-01-01T00:00
  interval: 1h

config:
  model_type: swan
  startup:
    project:
      name: First model
      nr: t01
    set:
      direction_convention: nautical
    coordinates:
      kind:
        model_type: spherical
  cgrid:
    model_type: regular
    grid: {xp: 110.0, yp: -36.0, xlen: 6.0, ylen: 7.0, mx: 12, my: 14}
    spectrum: {mdc: 36, flow: 0.04, fhigh: 1.0}
  inpgrid:
    model_type: data_interface
    bottom:
      var: bottom
      source:
        model_type: file
        uri: tests/data/gebco-1deg.nc
      z1: elevation
      fac: -1.0
      coords: {x: lon, y: lat}
      buffer: 1.0
  boundary:
    model_type: boundspec
    shapespec:
      shape:
        model_type: jonswap
        gamma: 3.3
      per_type: peak
      dspr_type: degrees
    location:
      model_type: side
      side: west
      direction: ccw
    data:
      model_type: constantpar
      hs: 2.0
      per: 12.0
      dir: 240.0
      dd: 20.0
  physics:
    gen:
      model_type: gen3
    deactivate:
      offs:
        - physics: quadrupl
  output:
    block:
      model_type: block
      sname: COMPGRID
      fname: swangrid.nc
      output: [depth, hsign, dir, tps]
  lockup:
    compute:
      model_type: compute
"""
CONFIG_FILE = Path(OUT_DIR) / "model.yml"
CONFIG_FILE.write_text(YAML_TEXT)
print(YAML_TEXT)
```

Relative paths, such as the bathymetry file and `output_dir`, are resolved from the folder Python or the `rompy` command runs in, not from the folder of the YAML file.

### Loading and validating YAML in Python

Loading the file into a `ModelRun` validates everything and builds the same objects as the Python code above:

```python exec="on" source="above" result="text" session="configuration"
import yaml

conf = yaml.safe_load(CONFIG_FILE.read_text())
modelrun = ModelRun(**conf)

print(type(modelrun.config.cgrid).__name__, type(modelrun.config.inpgrid).__name__)
print(modelrun.config.physics.render())
```

Mistakes are reported with the path to the offending field. Here the spectral grid has its frequencies the wrong way round:

```python exec="on" source="above" result="text" session="configuration"
from pydantic import ValidationError

bad = yaml.safe_load(CONFIG_FILE.read_text())
bad["config"]["cgrid"]["spectrum"]["flow"] = 1.5
try:
    ModelRun(**bad)
except ValidationError as error:
    for err in error.errors():
        print(".".join(str(loc) for loc in err["loc"]), "->", err["msg"])
```

The path starts with `config.swan`: rompy chooses the model class from `config.model_type`. Misspelt field names are rejected with a suggestion, for example `Unknown field 'phyiscs'. Did you mean 'physics'?`.

To load only the model part of a file, pass the `config` section to `SwanConfig`: `SwanConfig(**conf["config"])`.

### Choosing between classes: `model_type`

Where a field accepts more than one class, `model_type` names the one to use. It is required for the fields below, which SWAN's alternatives make more common than in other models, and optional elsewhere. In a `ModelRun` file, `config` itself needs `model_type: swan`; a dictionary passed straight to `SwanConfig` does not.

| Field | `model_type` values |
|---|---|
| `config` | `swan` |
| `cgrid` | `regular`, `curvilinear`, `unstructured` |
| `inpgrid` | `data_interface`, `inpgrids` |
| `inpgrid.bottom.source`, `inpgrid.input[].source` | rompy sources: `file`, `intake`, `datamesh`, ... |
| `boundary` | `boundspec`, `boundnest1`, `boundnest2`, `boundnest3`, `boundary_interface` |
| `boundary.kind` (in a `boundary_interface`) | `boundnest1`, `boundspecside`, `boundspecsegmentxy` |
| `startup.coordinates.kind` | `cartesian`, `spherical` |
| `physics.gen` | `gen1`, `gen2`, `gen3` |
| `physics.breaking` | `constant`, `bkd` |
| `physics.friction` | `jonswap`, `collins`, `madsen`, `ripples` |
| `physics.triad` | `triad`, `dcta`, `lta`, `spb` |
| `output.block`, `output.points` | `block`, `blocks`; `points`, `points_file` |
| `lockup.compute` | `compute` (stationary mode), `stat`, `nonstat` |

Each class shows its `model_type` with its fields in the [reference](../reference/index.md). An unknown value lists the valid ones; a missing one gives `Unable to extract tag using discriminator 'model_type'`:

```python exec="on" source="above" result="text" session="configuration"
bad = yaml.safe_load(CONFIG_FILE.read_text())
bad["config"]["physics"]["gen"]["model_type"] = "gen4"
try:
    ModelRun(**bad)
except ValidationError as error:
    print(error.errors()[0]["msg"])
```

### Generating from Python

A validated `ModelRun` is generated as before. The output folder is set to the temporary folder here:

```python exec="on" session="configuration"
# Hidden: write into the temporary folder rather than ./output.
conf["output_dir"] = OUT_DIR
modelrun = ModelRun(**conf)
```

```python exec="on" source="above" result="text" session="configuration"
workspace = Path(modelrun())
print(workspace.name, sorted(p.name for p in workspace.iterdir()))
```

## The `rompy` command line

rompy installs a `rompy` command that works on the same YAML file, with no Python code. Run it from the folder the relative paths refer to.

| Command | What it does |
|---|---|
| `rompy validate model.yml` | Loads and validates the file; exits with an error if anything is wrong |
| `rompy generate model.yml` | Writes the workspace; `--output-dir` overrides `output_dir` |
| `rompy run model.yml --backend-config backend.yml` | Generates the workspace and runs SWAN with a backend |
| `rompy schema` | Prints the JSON schema of the configuration |

```bash
rompy validate model.yml && echo "Configuration is valid"
rompy generate model.yml
```

`rompy run` also takes `--dry-run` (generate only) and `--skip-generate` (run a workspace generated earlier). The backend file, for example one that runs SWAN in Docker, is described in [Running SWAN](running.md#from-the-command-line).

When the command line reads a file, it also:

- replaces `${VAR}` with the value of the environment variable `VAR`, for example `uri: ${DATA_DIR}/gebco.nc`, and stops with an error if the variable is not set;
- supports `!include other.yml` to compose a configuration from several files.

These two features belong to the command line's file loader; `yaml.safe_load` in Python does not apply them.

## `SwanConfigComponents`

`SwanConfigComponents` is the former name of `SwanConfig`, kept for older code and YAML files. It behaves the same, with `model_type: swanconfig`, but emits a `DeprecationWarning` and will be removed in a future version. Replace it with `SwanConfig` and `model_type: swan`.

## See it in the notebooks

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["configuration", "declarative", "yaml", "cli"]))
```
