# Rompy-SWAN

**Python interface for the SWAN spectral wave model**

Rompy-swan provides a type-safe, Pythonic way to configure and run [SWAN](https://swanmodel.sourceforge.io/) simulations. It is part of the [rompy](https://github.com/rom-py/rompy) ecosystem for regional ocean modelling.

!!! info "About SWAN"
    SWAN (Simulating WAves Nearshore) is a third-generation spectral wave model developed at Delft University of Technology. It computes random, short-crested wind-generated waves in coastal regions and inland waters. SWAN accounts for wave propagation, refraction, shoaling, generation by wind, whitecapping, bottom friction, depth-induced breaking, and nonlinear wave-wave interactions.

## Features

- **Type-safe configuration** — Pydantic models validate parameters before running SWAN, catching errors early with clear messages
- **Command generation** — Automatic generation of SWAN input files from Python objects or YAML
- **Data interfaces** — Connect external data sources (NetCDF, THREDDS, local files) to SWAN input grids and boundaries
- **Structured organisation** — SWAN commands grouped into logical components for better discoverability
- **YAML support** — Define configurations declaratively for reproducibility
- **IDE support** — Full autocomplete and type hints in modern editors

## Quick Example

```python
from rompy_swan.config import SwanConfig
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.components.startup import PROJECT, SET, MODE, COORDINATES
from rompy_swan.components.physics import GEN3, BREAKING_CONSTANT, FRICTION_JONSWAP
from rompy_swan.components.numerics import PROP, NUMERIC
from rompy_swan.components.group import STARTUP, PHYSICS

config = SwanConfig(
    cgrid=REGULAR(
        spectrum=dict(mdc=36, flow=0.04, fhigh=1.0),
        grid=dict(xp=0, yp=0, alp=0, xlen=100000, ylen=50000, mx=100, my=50),
    ),
    startup=STARTUP(
        project=PROJECT(name="Example", nr="001"),
        set=SET(level=0.0),
        mode=MODE(),
        coordinates=COORDINATES(),
    ),
    physics=PHYSICS(
        gen=GEN3(),
        breaking=BREAKING_CONSTANT(alpha=1.0, gamma=0.73),
        friction=FRICTION_JONSWAP(cfjon=0.067),
    ),
)
```

This generates valid SWAN command input:

```
PROJECT 'Example' '001'
SET level=0.0
MODE NONSTATIONARY TWODIMENSIONAL
COORDINATES CARTESIAN
CGRID REGULAR 0 0 0 100000 50000 100 50 CIRCLE 36 0.04 1.0
GEN3
BREAKING CONSTANT alpha=1.0 gamma=0.73
FRICTION JONSWAP cfjon=0.067
```

## Why Rompy-SWAN?

SWAN uses a command-based input file format with many options and parameters. While flexible, this can be:

- **Error-prone** — Typos in command names or parameters cause runtime failures
- **Hard to discover** — Which commands exist? What are valid options?
- **Difficult to validate** — Invalid combinations only fail when SWAN runs

Rompy-swan addresses these by:

1. **Validating at construction** — Invalid values raise clear errors immediately
2. **Grouping related commands** — Find physics settings under `physics`, output under `output`
3. **Enforcing constraints** — Type checking ensures valid parameter combinations
4. **Providing defaults** — Sensible SWAN defaults with documentation

## Documentation Structure

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting Started**

    ---

    Install rompy-swan and run your first simulation

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)

-   :material-book-open-variant:{ .lg .middle } **Concepts**

    ---

    Learn the architecture and how to configure SWAN models

    [:octicons-arrow-right-24: Architecture](user-guide/architecture.md)

-   :material-puzzle:{ .lg .middle } **Components**

    ---

    Detailed reference for each component (Physics, Boundary, Output, etc.)

    [:octicons-arrow-right-24: Components](components/index.md)

-   :material-puzzle-outline:{ .lg .middle } **Subcomponents**

    ---

    Branching options within SWAN commands (locations, spectra, etc.)

    [:octicons-arrow-right-24: Subcomponents](subcomponents/base.md)

-   :material-database:{ .lg .middle } **Data Interfaces**

    ---

    Bridge external data sources with SWAN model inputs

    [:octicons-arrow-right-24: Data Interfaces](data-interfaces/index.md)

-   :material-notebook:{ .lg .middle } **Examples**

    ---

    Jupyter notebooks demonstrating common workflows

    [:octicons-arrow-right-24: Examples](examples/index.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete API documentation generated from source code

    [:octicons-arrow-right-24: API Reference](api-reference/config.md)

-   :material-account-group:{ .lg .middle } **Developer**

    ---

    Contributing guidelines and development setup

    [:octicons-arrow-right-24: Contributing](developer/contributing.md)

</div>

## Part of the Rompy Ecosystem

Rompy-swan is a plugin for [rompy](https://github.com/rom-py/rompy), the regional ocean modelling framework. Other model plugins include:

- [rompy-xbeach](https://github.com/rom-py/rompy-xbeach){:target="_blank"} — XBeach coastal morphodynamic model
- [rompy-schism](https://github.com/rom-py/rompy-schism){:target="_blank"} — SCHISM unstructured grid model

## Links

- [SWAN Documentation](https://swanmodel.sourceforge.io/online_doc/swanuse/swanuse.html){:target="_blank"}
- [SWAN Download](https://swanmodel.sourceforge.io/download/download.htm){:target="_blank"}
- [Rompy Core](https://rom-py.github.io/rompy/){:target="_blank"}