# Lock-up

Lock-up commands control the execution of SWAN calculations. They must appear at the end of the input file after all other commands.

!!! warning "Required Commands"
    Every SWAN input file must end with a `COMPUTE` command (to start the calculation) and a `STOP` command (to terminate SWAN).

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