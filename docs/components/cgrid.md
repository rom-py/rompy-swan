# Computational Grid

The computational grid (CGRID) defines the spatial and spectral discretization for SWAN calculations. It specifies where wave action densities are computed.

!!! info "Grid Types"
    SWAN supports three grid types:
    
    - **Regular** — Rectangular grid with uniform spacing
    - **Curvilinear** — Grid with curved coordinate lines (e.g., following coastlines)
    - **Unstructured** — Triangular mesh for complex geometries

The CGRID command also defines the spectral resolution (number of directions and frequency range).

## Regular Grid

::: rompy_swan.components.cgrid.REGULAR

## Curvilinear Grid

::: rompy_swan.components.cgrid.CURVILINEAR

## Unstructured Grid

::: rompy_swan.components.cgrid.UNSTRUCTURED