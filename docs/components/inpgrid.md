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

::: rompy_swan.components.inpgrid.WIND
::: rompy_swan.components.inpgrid.ICE