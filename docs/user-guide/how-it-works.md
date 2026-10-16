# How rompy-swan works

SWAN reads a command file, `INPUT`, whose commands come in a fixed order, plus input files for bathymetry, forcing and boundaries. rompy-swan builds these from a tree of validated objects, one per SWAN command. This page explains that tree, which parts come from rompy, and how the objects become the command file.

## The configuration tree

```text
ModelRun                      rompy: run id, period, output directory; generates and runs
└── config: SwanConfig        rompy-swan: the SWAN command file
    ├── startup               PROJECT, SET, MODE, COORDINATES
    ├── cgrid                 CGRID: computational and spectral grids (required)
    ├── inpgrid               INPGRID/READINP, or a DataInterface writing them from data
    ├── forcing               constant WIND and ICE
    ├── boundary              BOUNDSPEC, BOUNDNEST1/2/3, or a BoundaryInterface
    ├── initial               INITIAL
    ├── physics               GEN3, BREAKING, FRICTION, TRIAD, ...
    ├── prop                  PROP
    ├── numeric               NUMERIC
    ├── output                locations, QUANTITY, BLOCK, TABLE, SPECOUT, NESTOUT
    └── lockup                COMPUTE, HOTFILE, STOP
```

Each field of [`SwanConfig`][rompy_swan.config.SwanConfig] is a section of the command file, written in this order.

The objects fall into two kinds:

- **Components** are SWAN commands. Each class is named after its command (`CGRID`, `BOUNDSPEC`, `GEN3`, `BLOCK`), its fields are the command's options, and it renders exactly that command. Commands SWAN groups together, such as the physics commands, are given as a **group** ([`PHYSICS`][rompy_swan.components.group.PHYSICS], [`OUTPUT`][rompy_swan.components.group.OUTPUT] and others), which renders its commands in the right order and checks them together.
- **Interfaces** fill in what depends on the run. A [`DataInterface`][rompy_swan.interface.DataInterface] writes input grids from data sources and returns their `INPGRID` and `READINP` commands; a [`BoundaryInterface`][rompy_swan.interface.BoundaryInterface] writes boundary spectra from wave model output; in nonstationary mode, the computation and output times are set from the run period.

## What comes from rompy

rompy-swan builds on [rompy](https://rom-py.github.io/rompy/), which provides the parts shared by all models:

| rompy provides | Used in rompy-swan for |
|---|---|
| [`ModelRun`][rompy.model.ModelRun] | Generating the workspace and running SWAN |
| [`TimeRange`][rompy.core.time.TimeRange] | The run period: computation and output times in nonstationary mode, and the time range of input data |
| [`BaseConfig`][rompy.core.config.BaseConfig] | The base of [`SwanConfig`][rompy_swan.config.SwanConfig], with the `template` and `checkout` fields |
| [`RegularGrid`][rompy.core.grid.RegularGrid] | The base of [`SwanGrid`][rompy_swan.grid.SwanGrid] |
| [`DataGrid`][rompy.core.data.DataGrid] | The base of [`SwanDataGrid`][rompy_swan.data.SwanDataGrid], with the `source`, `filter`, `crop_data`, `buffer` and `time_buffer` fields |
| [`BoundaryWaveStation`][rompy.core.boundary.BoundaryWaveStation] | The base of the boundary data classes, which select spectra along the grid boundary |
| rompy sources, e.g. [`SourceFile`][rompy.core.source.SourceFile] | Reading data |
| Backends, e.g. [`DockerConfig`][rompy.backends.config.DockerConfig] | Running SWAN locally, in Docker or on a cluster |
| The `rompy` command line | Generating and running models from YAML |

The [reference](../reference/index.md) lists the fields each class inherits from rompy together with its own.

## From objects to commands

A component renders its command with `render()`. Options left unset are usually not written, and SWAN then uses its own default, which the field description gives:

```python exec="on" source="above" result="text"
from rompy_swan.components.physics import GEN1

print(GEN1().render())
print(GEN1(cf10=188.0, cdrag=0.0012).render())
```

Some fields default to SWAN's default value and write it explicitly, so the command file shows the choice. `GEN3` writes its default source terms, Westhuysen with Wu's wind drag:

```python exec="on" source="above" result="text"
from rompy_swan.components.physics import GEN3
from rompy_swan.subcomponents.physics import WESTHUYSEN

print(GEN3().render())
print(GEN3(source_terms=WESTHUYSEN(wind_drag="wu", agrow=True)).render())
```

Choices between variants are pydantic models told apart by their `model_type`, so only valid combinations can be built: `GEN3` takes one of the source term packages (`JANSSEN`, `KOMEN`, `WESTHUYSEN`, `ST6`), each with its own options. Lines longer than SWAN's limit of 132 characters are split with SWAN's continuation character `&`.

A group renders its commands in order:

```python exec="on" source="above" result="text"
from rompy_swan.components.group import PHYSICS
from rompy_swan.components.physics import BREAKING_CONSTANT, FRICTION_JONSWAP, GEN3

physics = PHYSICS(gen=GEN3(), breaking=BREAKING_CONSTANT(), friction=FRICTION_JONSWAP())
print(physics.render())
```

The [command index](../reference/commands.md) lists every SWAN command rompy-swan can write and the component that writes it.

## Generating the workspace

Calling a [`ModelRun`][rompy.model.ModelRun] generates the workspace. rompy calls the configuration with the run details, and [`SwanConfig`][rompy_swan.config.SwanConfig] then:

1. in nonstationary mode, sets the times of the output and computation commands from the run period;
2. renders each component and group;
3. calls the interfaces, which write the input grid and boundary files into the workspace and return their commands;
4. renders the command file, `INPUT`, from the template, one section per field.

The workspace folder, `output_dir/run_id`, is ready for SWAN to run.

## Validation

Mistakes are caught when the objects are created, before SWAN runs:

- **Types and ranges.** Each field checks its type and allowed range, and unknown fields are rejected with a suggestion:

    ```python exec="on" source="above" result="text"
    from rompy_swan.components.physics import GEN3

    try:
        GEN3(source_term="komen")
    except Exception as err:
        print(err)
    ```

- **Required options.** Each command requires the options SWAN requires, and `SwanConfig` requires a computational grid.
- **Combinations SWAN refuses.** `SwanConfig` checks settings that depend on each other. For example, in stationary mode, SWAN's default, there is a single computation without times, so timed inputs and outputs are rejected:

    ```python exec="on" source="above" result="text"
    from rompy_swan.components.cgrid import REGULAR
    from rompy_swan.components.group import LOCKUP
    from rompy_swan.components.lockup import COMPUTE_NONSTAT
    from rompy_swan.config import SwanConfig
    from rompy_swan.grid import SwanGrid
    from rompy_swan.subcomponents.spectrum import SPECTRUM

    grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)
    try:
        SwanConfig(
            cgrid=REGULAR(grid=grid.component, spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0)),
            lockup=LOCKUP(compute=COMPUTE_NONSTAT()),
        )
    except Exception as err:
        print(err)
    ```

[Stationary and nonstationary runs](modes.md) explains the two modes.
