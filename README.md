# rompy-swan

[![PyPI version](https://img.shields.io/pypi/v/rompy-swan.svg)](https://pypi.org/project/rompy-swan/)
[![Tests](https://github.com/rom-py/rompy-swan/actions/workflows/testing.yml/badge.svg)](https://github.com/rom-py/rompy-swan/actions/workflows/testing.yml)
[![Documentation](https://github.com/rom-py/rompy-swan/actions/workflows/build-docs.yml/badge.svg)](https://rom-py.github.io/rompy-swan/)
[![Python versions](https://img.shields.io/pypi/pyversions/rompy-swan)](https://pypi.org/project/rompy-swan/)

rompy-swan sets up and runs the [SWAN](https://swanmodel.sourceforge.io/) spectral wave model from Python or YAML. It is the SWAN plugin of [rompy](https://rom-py.github.io/rompy/), which provides the run period, data sources, model runs and backends shared by all models.

SWAN reads a command file, `INPUT`, whose commands come in a fixed order. rompy-swan describes each SWAN command as a validated Python object and writes the command file and its input files:

- **One component per SWAN command**: `CGRID`, `BOUNDSPEC`, `GEN3`, `BLOCK` and the others, with the same names and options as in the SWAN user manual.
- **Input grids and boundaries from data**: bathymetry, wind, currents and water levels from gridded datasets, and boundary spectra from wave model output.
- **Checks before SWAN runs**: invalid options and combinations SWAN refuses are caught when the configuration is built.
- **Times from the run**: in nonstationary mode, computation and output times come from the run period.

## Documentation

- Documentation: https://rom-py.github.io/rompy-swan/
- Tutorial and examples (notebooks): https://rom-py.github.io/rompy-notebooks/swan-tutorial/
- Changelog: [HISTORY.rst](https://github.com/rom-py/rompy-swan/blob/main/HISTORY.rst)

## Installation

```bash
pip install rompy-swan
```

SWAN itself is not included. The public Docker image `ghcr.io/rom-py/swan` runs the generated workspaces, with NetCDF output; see [Running SWAN](https://rom-py.github.io/rompy-swan/user-guide/running/).

## Contributing

See the [contributing guide](https://rom-py.github.io/rompy-swan/development/contributing/).

## License

Apache Software License 2.0. See [LICENSE](https://github.com/rom-py/rompy-swan/blob/main/LICENSE).
