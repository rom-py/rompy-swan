# Boundary and Initial Conditions

Boundary conditions specify wave energy entering the computational domain. Initial conditions define the starting wave field for non-stationary simulations.

!!! info "Boundary Types"
    - **BOUNDSPEC** — Parametric or spectral boundary conditions at domain edges
    - **BOUNDNEST1/2/3** — Nested boundary conditions from coarser SWAN runs (different nesting levels)

## Boundary Conditions

### BOUNDSPEC

Specifies wave conditions at the boundary using parametric (Hs, Tp, direction) or spectral data.

::: rompy_swan.components.boundary.BOUNDSPEC

### Nested Boundaries

For nested simulations, use output from a coarser SWAN run as boundary input.

::: rompy_swan.components.boundary.BOUNDNEST1
::: rompy_swan.components.boundary.BOUNDNEST2
::: rompy_swan.components.boundary.BOUNDNEST3

## Initial Conditions

For non-stationary runs, the initial wave field can significantly affect early results. SWAN can start from rest, use a JONSWAP spectrum, or read from a previous run.

::: rompy_swan.components.boundary.INITIAL