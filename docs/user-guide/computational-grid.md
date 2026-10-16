# Computational grid

SWAN computes on the computational grid, set with its [`CGRID`](https://swanmodel.sourceforge.io/online_doc/swanuse/swanuse.html) command: the geographic grid where the wave field is computed and, at every grid point, the spectral grid of directions and frequencies. In rompy-swan the computational grid is the `cgrid` field of [`SwanConfig`][rompy_swan.config.SwanConfig], its only required field. This page covers regular grids and [`SwanGrid`][rompy_swan.grid.SwanGrid], the coordinate system, the spectral grid, and the curvilinear and unstructured grids SWAN also supports.

## A regular grid

A [`SwanGrid`][rompy_swan.grid.SwanGrid] places a regular grid by its origin (`x0`, `y0`), spacing (`dx`, `dy`), number of points (`nx`, `ny`) and rotation (`rot`). It is a rompy grid, which the data and boundary interfaces use to crop input data and to find boundary points.

SWAN describes the same grid differently, by its length and number of *meshes*, the cells between points. `grid.component` converts it into the grid part of the `CGRID` command, a [`GRIDREGULAR`][rompy_swan.subcomponents.readgrid.GRIDREGULAR]:

```python exec="on" source="above" result="text" session="cgrid"
from rompy_swan.grid import SwanGrid

grid = SwanGrid(x0=110.0, y0=-36.0, dx=0.5, dy=0.5, nx=13, ny=15)
print(grid.component.render())
```

| `SwanGrid` | `CGRID REGULAR` | Relation |
|---|---|---|
| `x0`, `y0` | `xpc`, `ypc` | origin, the lower-left corner when `rot=0` |
| `rot` | `alpc` | direction of the x-axis, degrees anticlockwise from east |
| `nx`, `ny` (points) | `mxc`, `myc` (meshes) | `mxc = nx - 1`, `myc = ny - 1` |
| `dx`, `dy` | `xlenc`, `ylenc` | `xlenc = dx * (nx - 1)`, `ylenc = dy * (ny - 1)` |

The `CGRID` component for a regular grid is [`REGULAR`][rompy_swan.components.cgrid.REGULAR], which combines the grid and the spectral grid (see [below](#the-spectral-grid)):

```python exec="on" source="above" result="text" session="cgrid"
from rompy_swan.components.cgrid import REGULAR
from rompy_swan.subcomponents.spectrum import SPECTRUM

cgrid = REGULAR(grid=grid.component, spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0))
print(cgrid.render())
```

`REGULAR` stores SWAN's values, not the `SwanGrid`, so a YAML file gives the grid as `xp`, `yp`, `alp`, `xlen`, `ylen`, `mx` and `my` (see [Configuration](configuration.md#the-same-model-as-yaml)). `SwanConfig.grid` converts them back into a `SwanGrid` for the interfaces:

```python exec="on" source="above" result="text" session="cgrid"
from rompy_swan.config import SwanConfig

config = SwanConfig(cgrid=cgrid)
print(config.grid, [float(v) for v in config.grid.bbox()])
```

`SwanGrid` also gives the coordinates of its points (`grid.x`, `grid.y`), its bounding box (`grid.bbox(buffer=...)`) and points along its boundary (`grid.boundary_points(spacing=...)`), which are useful for plotting and for checking that input data covers the grid.

## Spherical or Cartesian coordinates

[`COORDINATES`][rompy_swan.components.startup.COORDINATES], in the `startup` group, sets how SWAN reads every position in the command file:

```python exec="on" source="above" result="text" session="cgrid"
from rompy_swan.components.startup import COORDINATES
from rompy_swan.subcomponents.startup import CARTESIAN, SPHERICAL

print(COORDINATES(kind=SPHERICAL()).render())
print(COORDINATES(kind=SPHERICAL(projection="qc")).render())
print(COORDINATES(kind=CARTESIAN()).render())
```

| Coordinates | Positions and spacing | Rotation | Use for |
|---|---|---|---|
| [`SPHERICAL`][rompy_swan.subcomponents.startup.SPHERICAL] | longitude and latitude, in degrees | none: regular grids must be aligned with the meridians (`alpc=0`) | regional domains, and any model nested in a global one |
| [`CARTESIAN`][rompy_swan.subcomponents.startup.CARTESIAN] (SWAN's default) | metres, in a projected system such as UTM | `rot`, to align the grid with the coast | local domains |

A rotated grid in projected coordinates, in metres:

```python exec="on" source="above" result="text" session="cgrid"
utm_grid = SwanGrid(x0=370000.0, y0=6360000.0, rot=15.0, dx=200.0, dy=200.0, nx=101, ny=81)
print(utm_grid.component.render())
```

!!! warning "rompy-swan does not reproject data"
    The data and boundary interfaces take coordinates from the datasets as they are. With Cartesian coordinates, bathymetry, wind and boundary spectra must be in the same projected system as the grid. rompy-swan also does not check that a spherical grid has no rotation: keep `rot=0` with `SPHERICAL`.

Without `COORDINATES`, SWAN assumes Cartesian coordinates. A model in longitude and latitude must therefore set `COORDINATES(kind=SPHERICAL())`.

## Directions and rotation

SWAN's default direction convention is Cartesian: the direction waves travel *to*, anticlockwise from the x-axis. [`SET`][rompy_swan.components.startup.SET] with `direction_convention="nautical"` switches wave and wind directions, in the command file and in the output, to the direction they come *from*, clockwise from north:

```python exec="on" source="above" result="text" session="cgrid"
from rompy_swan.components.startup import SET

print(SET(direction_convention="nautical").render())
print(SET(direction_convention="cartesian").render())
```

The convention applies to boundary wave directions, constant wind directions, spectral sectors and output directions. Grid rotations (`alpc`, `alpinp`) always follow the Cartesian convention, whatever `SET` says.

## The spectral grid

At every grid point SWAN resolves the wave spectrum over directions and frequencies. [`SPECTRUM`][rompy_swan.subcomponents.spectrum.SPECTRUM] sets this resolution, the second part of the `CGRID` command:

- [`mdc`][rompy_swan.subcomponents.spectrum.SPECTRUM.mdc]: the number of directional bins, e.g. 36 over the full circle gives 10° bins.
- [`flow`][rompy_swan.subcomponents.spectrum.SPECTRUM.flow], [`fhigh`][rompy_swan.subcomponents.spectrum.SPECTRUM.fhigh] and [`msc`][rompy_swan.subcomponents.spectrum.SPECTRUM.msc]: the lowest and highest frequencies and the number of frequency meshes (one less than the number of frequencies). Give two of them and SWAN computes the third so the frequencies are spaced logarithmically, about 10% apart, as its quadruplet approximation (DIA) assumes.

```python exec="on" source="above" result="text" session="cgrid"
print(SPECTRUM(mdc=36, flow=0.04, fhigh=1.0).render())
print(SPECTRUM(mdc=36, flow=0.04, msc=33).render())
```

With 0.04 to 1 Hz, SWAN uses 34 meshes, i.e. 35 frequencies; its `PRINT` file reports them as `MSC-1 = 34`. The [SWAN manual](https://swanmodel.sourceforge.io/online_doc/swanuse/node11.html) suggests:

| Setting | Guidance |
|---|---|
| Directions | 10–15° for wind sea (`mdc=24` to `36` over the circle), 2–5° for narrow swell |
| `flow` | below 0.7 times the lowest peak frequency expected; 0.03–0.04 Hz for ocean swell |
| `fhigh` | 1 Hz is usually enough; at least 2.5–3 times the highest peak frequency |

### Circle or sector

By default the directions cover the full circle (`CIRCLE`). When all waves come from one side, a `SECTOR` from `dir1` to `dir2` saves computation; energy outside the sector is ignored. `mdc` then divides the sector, not the circle:

```python exec="on" source="above" result="text" session="cgrid"
print(SPECTRUM(mdc=18, dir1=180.0, dir2=360.0, flow=0.04, fhigh=1.0).render())
```

The sector directions follow the convention set by `SET`. Use a sector only when no significant energy travels outside it; locally generated wind sea can grow in any direction.

The spectral settings are checked when the object is created:

```python exec="on" source="above" result="text" session="cgrid"
from pydantic import ValidationError

for kwargs in [dict(flow=1.0, fhigh=0.04), dict(flow=0.04), dict(flow=0.04, fhigh=1.0, dir1=180.0)]:
    try:
        SPECTRUM(mdc=36, **kwargs)
    except ValidationError as err:
        print(err.errors()[0]["msg"])
```

## Curvilinear and unstructured grids

SWAN also computes on curvilinear grids, which follow a coastline or a channel, and on unstructured triangular meshes, which refine resolution where it is needed. Both read their geometry from files that you provide; rompy-swan writes the commands.

[`CURVILINEAR`][rompy_swan.components.cgrid.CURVILINEAR] gives the number of meshes and reads the coordinates of the `mxc + 1` by `myc + 1` points with [`READCOORD`][rompy_swan.subcomponents.readgrid.READCOORD]. `xexc` and `yexc` mark points to ignore, for example on land:

```python exec="on" source="above" result="text" session="cgrid"
from rompy_swan.components.cgrid import CURVILINEAR
from rompy_swan.subcomponents.readgrid import READCOORD

curvilinear = CURVILINEAR(
    mxc=199,
    myc=99,
    xexc=-999.0,
    yexc=-999.0,
    readcoord=READCOORD(fname="grid_coord.txt"),
    spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0),
)
print(curvilinear.render())
```

[`UNSTRUCTURED`][rompy_swan.components.cgrid.UNSTRUCTURED] reads a mesh written by ADCIRC (`fort.14`, no file name), Triangle or Easymesh (a base file name):

```python exec="on" source="above" result="text" session="cgrid"
from rompy_swan.components.cgrid import UNSTRUCTURED

print(UNSTRUCTURED(grid_type="adcirc", spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0)).render())
print(UNSTRUCTURED(grid_type="triangle", fname="mesh", spectrum=SPECTRUM(mdc=36, flow=0.04, fhigh=1.0)).render())
```

The data and boundary interfaces crop data and choose boundary points on a `SwanGrid`, so they need a `REGULAR` grid:

| Feature | `REGULAR` | `CURVILINEAR`, `UNSTRUCTURED` |
|---|---|---|
| `CGRID` command | yes | yes |
| `DataInterface` (input grids from data) | yes | no: write the input grids with `INPGRIDS` ([Input grids and forcing](input-grids.md#hand-written-input-grids)) |
| `BoundaryInterface` (boundary spectra from data) | yes | no: use `BOUNDSPEC` or `BOUNDNEST` ([Boundary and initial conditions](boundaries.md)) |
| Physics, numerics, output | yes | yes |

With a curvilinear or unstructured grid, a configuration that uses an interface is accepted but fails when the workspace is generated.

## See it in the notebooks

```python exec="on"
from rompy_docs.notebooks import see_also

print(see_also("swan", ["grid", "spectrum"]))
```
