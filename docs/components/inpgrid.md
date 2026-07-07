# Input Grids

Input grids (INPGRID) define the spatial grids for external forcing data such as bathymetry, wind, currents, water level, and friction. Each input grid can have different resolution and extent from the computational grid.

!!! info "Input Grid Types"
    - **BOTTOM** — Bathymetry (water depth)
    - **WIND** — Wind velocity components
    - **CURRENT** — Current velocity components
    - **WLEVEL** — Water level variations
    - **FRICTION** — Spatially varying bottom friction
    - **ICE** — Sea ice coverage

## Grid Types

::: rompy_swan.components.inpgrid.REGULAR
::: rompy_swan.components.inpgrid.CURVILINEAR
::: rompy_swan.components.inpgrid.UNSTRUCTURED

## Specialized Grids

!!! warning "Deprecation notice"
    `WIND` and `ICE` inside `INPGRIDS` (i.e. as entries in `inpgrid`) are deprecated. For constant, spatially-uniform wind or ice forcing use [`SwanConfig.forcing`](../user-guide/configuration.md#forcing) with the [`FORCING`](group.md) group component instead. Gridded, time-varying wind/ice should be supplied via `DataInterface`.

::: rompy_swan.components.inpgrid.WIND
::: rompy_swan.components.inpgrid.ICE