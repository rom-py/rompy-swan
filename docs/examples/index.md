# Examples

These notebooks demonstrate common rompy-swan workflows.

## Getting Started

<div class="grid cards" markdown>

-   :material-file-document-edit:{ .lg .middle } **Declarative Configuration**

    ---

    Configure SWAN simulations using YAML files for reproducible workflows.

    [:octicons-arrow-right-24: View notebook](example_declarative.ipynb)

-   :material-code-braces:{ .lg .middle } **Procedural Configuration**

    ---

    Build SWAN configurations programmatically using Python for dynamic setups.

    [:octicons-arrow-right-24: View notebook](example_procedural.ipynb)

-   :material-chart-line:{ .lg .middle } **Sensitivity Analysis**

    ---

    Run parameter sensitivity studies by varying configuration values.

    [:octicons-arrow-right-24: View notebook](example_sensitivity.ipynb)

</div>

## Boundary Conditions

<div class="grid cards" markdown>

-   :material-border-left-variant:{ .lg .middle } **BOUNDSPEC Side**

    ---

    Apply boundary conditions to entire domain sides.

    [:octicons-arrow-right-24: View notebook](boundary/boundspec_side.ipynb)

-   :material-vector-line:{ .lg .middle } **BOUNDSPEC Segment**

    ---

    Apply boundary conditions to specific segments.

    [:octicons-arrow-right-24: View notebook](boundary/boundspec_segment.ipynb)

-   :material-layers-outline:{ .lg .middle } **BOUNDNEST1**

    ---

    Nested boundary conditions from coarser SWAN runs.

    [:octicons-arrow-right-24: View notebook](boundary/boundnest1.ipynb)

</div>

## Components

<div class="grid cards" markdown>

-   :material-file-export:{ .lg .middle } **Output**

    ---

    Configure SWAN output options (BLOCK, TABLE, SPECOUT).

    [:octicons-arrow-right-24: View notebook](components/output.ipynb)

-   :material-grid:{ .lg .middle } **CGRID**

    ---

    Define computational grids (REGULAR, CURVILINEAR, UNSTRUCTURED).

    [:octicons-arrow-right-24: View notebook](components/cgrid.ipynb)

-   :material-cog-play:{ .lg .middle } **Startup**

    ---

    Initialize SWAN runs (PROJECT, SET, MODE, COORDINATES).

    [:octicons-arrow-right-24: View notebook](components/startup.ipynb)

-   :material-waves:{ .lg .middle } **Physics**

    ---

    Configure physical processes (generation, breaking, friction).

    [:octicons-arrow-right-24: View notebook](components/physics.ipynb)

-   :material-calculator:{ .lg .middle } **Numerics**

    ---

    Set numerical schemes and iteration settings (PROP, NUMERIC).

    [:octicons-arrow-right-24: View notebook](components/numerics.ipynb)

-   :material-database-import:{ .lg .middle } **INPGRID**

    ---

    Define input grids for forcing data (bathymetry, wind, currents).

    [:octicons-arrow-right-24: View notebook](components/inpgrid.ipynb)

</div>

## Running the Examples

To run these notebooks locally:

```bash
# Clone the notebooks repository
git clone https://github.com/rom-py/rompy-notebooks.git

# Install dependencies
pip install rompy-swan jupyter

# Navigate to SWAN examples
cd rompy-notebooks/notebooks/swan

# Start Jupyter
jupyter notebook
```

!!! note "SWAN Executable Required"
    These examples require a working SWAN installation. See the [installation guide](../getting-started/installation.md) for setup instructions.
