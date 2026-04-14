# Installation

## Requirements

- Python 3.9 or higher
- [SWAN](https://swanmodel.sourceforge.io/) executable (for running simulations)

## Install from PyPI

```bash
pip install rompy-swan
```

## Install from Source

For development or to get the latest features:

```bash
git clone https://github.com/rom-py/rompy-swan.git
cd rompy-swan
pip install -e ".[dev]"
```

## Verify Installation

```python
from rompy_swan import SwanConfig
print("rompy-swan installed successfully!")
```

## SWAN Executable

Rompy-swan generates SWAN input files but requires the SWAN executable to run simulations. Download SWAN from the [official website](https://swanmodel.sourceforge.io/download/download.htm).

After installation, ensure the `swan` executable is in your PATH:

```bash
swan --version
```

## Dependencies

Rompy-swan automatically installs:

- **rompy** — Core rompy framework
- **pydantic** — Data validation
- **numpy** — Numerical operations
- **xarray** — NetCDF data handling

## Next Steps

- [Quickstart](quickstart.md) — Run your first SWAN simulation
- [Architecture](../user-guide/architecture.md) — Understand the component structure
