# rompy-swan

rompy-swan sets up and runs the [SWAN](https://swanmodel.sourceforge.io/) spectral wave model from Python or YAML. It is the SWAN plugin of [rompy](https://rom-py.github.io/rompy/), which provides the parts every model shares: the run period, data sources, model runs and backends.

SWAN reads a command file, `INPUT`, whose commands come in a fixed order. rompy-swan describes each SWAN command as a validated Python object, and writes the command file and its input files for you:

- **One component per SWAN command.** `CGRID`, `BOUNDSPEC`, `GEN3`, `BLOCK` and the other commands are typed objects with the same names and options as in the [SWAN user manual](https://swanmodel.sourceforge.io/online_doc/swanuse/swanuse.html). Each renders exactly its command.
- **Input grids and boundaries from data.** Bathymetry, wind, currents and water levels come from gridded datasets, and boundary spectra from wave model output, cropped to the grid and the run period.
- **Checks before SWAN runs.** Invalid options are rejected when the objects are created, and combinations SWAN refuses, such as timed inputs in stationary mode, are caught before the run.
- **Times from the run.** In nonstationary mode, computation and output times are set from the run period.

```python
from rompy.core.time import TimeRange
from rompy.model import ModelRun
from rompy_swan.config import SwanConfig

config = SwanConfig(
    cgrid=cgrid,          # CGRID: the computational and spectral grids
    inpgrid=inpgrid,      # INPGRID/READINP: bathymetry and other input grids
    boundary=boundary,    # BOUNDSPEC/BOUNDNEST: waves entering the domain
    physics=physics,      # GEN3, BREAKING, FRICTION, ...
    output=output,        # BLOCK, TABLE, SPECOUT
)
run = ModelRun(
    run_id="swell",
    period=TimeRange(start="2023-01-01T00", end="2023-01-01T00", interval="1h"),
    output_dir="runs",
    config=config,
)
run()  # writes INPUT and the input files to runs/swell
```

[Your first model](getting-started/first-model.md) builds this example in full.

## Where to go next

| If you want to | Go to |
|---|---|
| Install rompy-swan and SWAN | [Installation](getting-started/installation.md) |
| Build a model in five minutes | [Your first model](getting-started/first-model.md) |
| Learn step by step, with notebooks | [Tutorial](tutorial.md) |
| Understand how the configuration maps to the SWAN command file | [How rompy-swan works](user-guide/how-it-works.md) |
| Set up a specific part of the model | The [User guide](user-guide/configuration.md) |
| Find the component for a SWAN command | [Command index](reference/commands.md) |
| Look up a class | [Reference](reference/index.md) |

rompy-swan is one of the rompy model plugins, with [rompy-xbeach](https://rom-py.github.io/rompy-xbeach/) and [rompy-schism](https://rom-py.github.io/rompy-schism/). The [rompy docs](https://rom-py.github.io/rompy/) explain the ideas they share.
