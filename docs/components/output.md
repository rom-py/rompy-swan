# Output

Output commands define where and what SWAN writes as results. Output can be written at specific locations (points, curves, grids) and in various formats (tables, blocks, spectra).

!!! info "Output Types"
    - **Locations** — Define where to extract output (points, curves, frames, nested grids)
    - **Quantities** — Configure output variable settings (units, exceptions)
    - **Write commands** — Specify output format and file names (BLOCK, TABLE, SPECOUT)

!!! note "Time Control for Output Components"
    When using the rompy API, output write commands (BLOCK, TABLE, SPECOUT, NESTOUT) have their start time (`tbeg`) set from the `ModelRun.period.start`. However, you can override the time interval (`delt`) and formatting (`tfmt`, `dfmt`) by specifying a `times` field in the component. If no `times` field is provided, the component uses the runtime interval.
    
    **Example:**
    ```python
    block=dict(
        sname="COMPGRID",
        fname="output.nc",
        output=["hsign"],
        times=dict(
            delt=timedelta(minutes=30),  # Custom interval
            tfmt=1,                       # ISO format
            dfmt="min",                   # Minutes
        ),
    )
    ```
    
    See the [Configuration Guide](../user-guide/configuration.md#time-control) for more details.

## Locations

::: rompy_swan.components.output.BaseLocation
::: rompy_swan.components.output.FRAME
::: rompy_swan.components.output.GROUP
::: rompy_swan.components.output.CURVE
::: rompy_swan.components.output.CURVES
::: rompy_swan.components.output.RAY
::: rompy_swan.components.output.ISOLINE
::: rompy_swan.components.output.POINTS
::: rompy_swan.components.output.POINTS_FILE
::: rompy_swan.components.output.NGRID
::: rompy_swan.components.output.NGRID_UNSTRUCTURED

## Settings

::: rompy_swan.components.output.QUANTITY
::: rompy_swan.components.output.QUANTITIES
::: rompy_swan.components.output.OUTPUT_OPTIONS

## Write

::: rompy_swan.components.output.BaseWrite
::: rompy_swan.components.output.BLOCK
::: rompy_swan.components.output.TABLE
::: rompy_swan.components.output.SPECOUT
::: rompy_swan.components.output.NESTOUT
::: rompy_swan.components.output.TEST