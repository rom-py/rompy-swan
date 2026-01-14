# Examples

These notebooks demonstrate common rompy-swan workflows.

## Available Examples

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
