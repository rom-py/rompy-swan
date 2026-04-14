# Lock-up

Lock-up commands control the execution of SWAN calculations. They must appear at the end of the input file after all other commands.

!!! warning "Required Commands"
    Every SWAN input file must end with a `COMPUTE` command (to start the calculation) and a `STOP` command (to terminate SWAN).

!!! note "Time Control for COMPUTE Components"
    When using the rompy API, COMPUTE commands have their time values (`tbeg`, `tend`, `delt`) set from the `ModelRun.period` runtime parameter. However, you can override the time and interval formatting (`tfmt`, `dfmt`) by specifying a `times` field in the component. The actual computational timestep (`deltc`) is always determined by the runtime interval.
    
    **Example:**
    ```python
    compute=dict(
        model_type="nonstat",
        times=dict(
            tfmt=2,      # HP compiler format: '01-Jan-24 00:00:00'
            dfmt="min",  # Minutes format
        ),
    )
    ```
    
    See the [Configuration Guide](../user-guide/configuration.md#time-control) for more details.

## COMPUTE

Starts the wave computation. For non-stationary runs, specifies the time stepping.

::: rompy_swan.components.lockup.COMPUTE
::: rompy_swan.components.lockup.COMPUTE_STAT
::: rompy_swan.components.lockup.COMPUTE_NONSTAT

## HOTFILE

Writes a hotstart file for continuing simulations later.

::: rompy_swan.components.lockup.HOTFILE

## STOP

Terminates SWAN execution.

::: rompy_swan.components.lockup.STOP