# Numerics

Numerics commands control the numerical schemes used for wave propagation and source term integration.

!!! tip "Default Numerics"
    SWAN uses robust default numerical settings. Only modify these if you understand the implications for accuracy and stability.

## PROP

Specifies the propagation scheme for geographic and spectral space.

::: rompy_swan.components.numerics.PROP

## NUMERIC

Controls iteration settings, accuracy criteria, and limiter options.

::: rompy_swan.components.numerics.NUMERIC