# Troubleshooting

Common problems when setting up and running SWAN with rompy-swan, grouped by where they show up: when the configuration is built, when the workspace is generated, and when SWAN runs. Each entry gives the cause and the fix, with a link to the page that covers the topic.

## When the configuration is built

### `Unknown field 'phyiscs'. Did you mean 'physics'?`

A field name is misspelt or does not exist on that class. The message suggests the closest field name. Field names follow the SWAN manual's option names where possible; check the class in the [reference](../reference/index.md). → [Configuration](configuration.md)

### `Input tag '...' found using 'model_type' does not match any of the expected tags`

The `model_type` of a nested object is misspelt, or belongs to a class the field does not accept. The message lists the valid values. If the message says `Unable to extract tag using discriminator 'model_type'`, the YAML leaves `model_type` out where a field accepts several classes, for example `cgrid`, `boundary`, `physics.gen`, `output.block` or `lockup.compute`. → [Configuration](configuration.md#choosing-between-classes-model_type)

### `Field required` for `cgrid`

`cgrid` is the only required field of `SwanConfig`: the computational grid, which the interfaces also use. → [Computational grid](computational-grid.md)

### `In stationary mode (MODE STATIONARY, SWAN's default) SWAN makes a single computation without times`

The configuration has no `startup.mode`, so SWAN runs in stationary mode, but asks for a computation at given times (`COMPUTE_STAT` or `COMPUTE_NONSTAT`). Either use `lockup=LOCKUP(compute=COMPUTE())`, or set `startup.mode=MODE(kind="nonstationary")`. → [Stationary and nonstationary runs](modes.md)

### `SWAN does not accept time information, used by ..., in stationary mode`

Output components with `times`, the boundary interface, and data interface inputs other than the bottom all write times, which SWAN refuses in stationary mode. Set `startup.mode=MODE(kind="nonstationary")`. For a single stationary computation with these inputs, use `MODE NONSTATIONARY` with `COMPUTE_STAT`: it computes the wave field in equilibrium with the conditions at the start of the run period. → [Stationary and nonstationary runs](modes.md)

### `COMPUTE is the single computation of stationary mode`

The reverse: `MODE NONSTATIONARY` with `COMPUTE`. In nonstationary mode, use `COMPUTE_STAT` or `COMPUTE_NONSTAT`, whose times are set from the run period. → [Stationary and nonstationary runs](modes.md)

### `You must specify at least 2 of [flow, fhigh, msc]` or `flow must be less than fhigh`

The spectral grid needs two of the lowest frequency, the highest frequency and the number of frequency meshes; SWAN computes the third. → [Computational grid](computational-grid.md#the-spectral-grid)

### `Specifying WIND inside INPGRIDS is deprecated`

Constant wind and ice now go in the `forcing` field, as a `FORCING` group, which can also be combined with a data interface. → [Input grids and forcing](input-grids.md#constant-wind-and-ice)

## When the workspace is generated

### `The input grid has 0 point along '...' but SWAN needs at least two`

The data, cropped to the computational grid plus `buffer`, has fewer than two points along an axis. This happens with data coarser than the model: increase the `buffer` of the `SwanDataGrid` to at least one data spacing. It also happens when the latitudes of the dataset run north to south, as in ERA5, which the crop does not expect: sort them with `filter={"sort": {"coords": ["latitude"]}}`. → [Input grids and forcing](input-grids.md#covering-the-computational-grid)

### The input grid does not cover the computational grid

Without an error, the `INPGRID` command can still describe a grid smaller than the computational grid, when only the data points inside the cropped box are kept. Compare the origin and extent in `INPGRID` with the grid's `bbox()`, and increase `buffer` until the input grid covers it. → [Input grids and forcing](input-grids.md#covering-the-computational-grid)

### `Nonstationary ... input needs at least two times`

Every input grid other than the bottom is written as a time series and needs at least two times within the run period. Check that the data covers the period; with data less frequent than the run, `time_buffer=[1, 1]` adds the data times on either side. A field that does not change, such as a friction map, also needs a time coordinate with two times, or can be written by hand with `INPGRIDS`. → [Input grids and forcing](input-grids.md#which-fields)

### A variable or coordinate is not found in the source

`coords` defaults to `longitude`, `latitude` and `time`, and `z1`/`z2` must be variable names in the dataset. Set them to the names in your data, for example `coords={"x": "lon", "y": "lat"}`. → [Input grids and forcing](input-grids.md#input-grids-from-data)

### `'CURVILINEAR' object has no attribute 'grid'`

The data and boundary interfaces need a regular computational grid. With a curvilinear or unstructured grid, write the input grids with `INPGRIDS` and the boundaries with `BOUNDSPEC` or `BOUNDNEST`. → [Computational grid](computational-grid.md#curvilinear-and-unstructured-grids)

### File paths are not found when running from YAML

Relative paths in a YAML file are resolved from the folder Python or the `rompy` command runs in, not from the folder of the YAML file. Run from the folder the paths refer to, or use absolute paths or `${VAR}` environment variables. → [Configuration](configuration.md#the-rompy-command-line)

## When SWAN runs

### SWAN computes nothing, but the run reports success

SWAN can stop before computing because of an error and still end normally: the backend returns `True` and SWAN writes `norm_end`. The reason is in `PRINT` (and `Errfile`), on lines starting with `** Error`. Always check `PRINT` after a run. → [Running SWAN](running.md#checking-a-run)

### `It is not recommended to use quadruplets in combination with zero wind conditions`

Quadruplet interactions are on by default with `GEN3`, and SWAN refuses them without wind. In a model without wind, switch them off:

```python
from rompy_swan.components.group import PHYSICS
from rompy_swan.components.physics import GEN3, OFF, OFFS

physics = PHYSICS(gen=GEN3(), deactivate=OFFS(offs=[OFF(physics="quadrupl")]))
```

→ [Physics](physics.md)

### A shadow spreads from the corners of the grid

SWAN only knows the waves that enter through the boundaries. On a boundary without wave information it assumes no waves come in, so when only one side is forced, wave energy is missing along the other sides and a shadow spreads into the domain from the corners. Give waves on every open boundary, for example with boundary spectra from a wave model, or place the unforced boundaries far from the area of interest. → [Boundary and initial conditions](boundaries.md)

### Waves or wind come from the wrong direction

SWAN's default direction convention is Cartesian: the direction waves and wind travel *to*, anticlockwise from east. Directions in the coming-*from*, clockwise-from-north sense, as in most datasets and buoy records, need `SET(direction_convention="nautical")` in `startup`. Grid rotations always use the Cartesian convention. → [Computational grid](computational-grid.md#directions-and-rotation)

### Results make no sense on a longitude–latitude grid

Without `COORDINATES SPHERICAL`, SWAN assumes Cartesian coordinates and reads a grid in degrees as metres. Set `startup.coordinates=COORDINATES(kind=SPHERICAL())` for grids in longitude and latitude, keep `rot=0` (SWAN requires regular spherical grids to be aligned with the meridians, and rompy-swan does not check it), and give all inputs in the same coordinates. → [Computational grid](computational-grid.md#spherical-or-cartesian-coordinates)

### A `BOUNDSPEC SEGMENT IJ` stops early

SWAN ends a segment given by grid indices at the first negative index. In rompy-swan, `-1` stands for the last index along an axis and is replaced with `mxc` or `myc` from the computational grid; other negative values are written as they are. → [Boundary and initial conditions](boundaries.md)

### `.nc` output files cannot be opened

SWAN built without NetCDF, such as the official `delftwaves/swan` image, writes `BLOCK` and `SPECOUT` files ending in `.nc` as text. Use the `ghcr.io/rom-py/swan` image or a SWAN build with NetCDF. → [Running SWAN](running.md#with-docker)

### There is no `PRINT` file, but `PRINT-001`, `PRINT-002`, ...

SWAN ran with MPI and wrote one log per process. Check each of them for errors. → [Running SWAN](running.md#in-parallel-with-mpi)

### `There are not enough slots available in the system`

Open MPI was asked for more processes than the machine has cores. Lower `cpu`, or, when running the image yourself, add `--oversubscribe` after `mpirun`. → [Running SWAN](running.md#in-parallel-with-mpi)

### Output files in the workspace are owned by root

The Docker container runs as root, so on Linux the files SWAN writes are owned by root. Remove or change them with `sudo`, or run the image yourself with `docker run --user "$(id -u):$(id -g)"`. → [Running SWAN](running.md#docker-without-rompy)

## See it in the notebooks

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["execution", "configuration"]))
```
