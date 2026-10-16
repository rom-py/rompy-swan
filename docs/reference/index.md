# API reference

The reference is generated from the rompy-swan source code. Each class lists all its fields, including those it inherits from [rompy](https://rom-py.github.io/rompy/reference/), with their types, defaults and descriptions. Most classes are SWAN commands: their docstring shows the command syntax and an example of what they write, and the [command index](commands.md) finds the component for a given command.

| Page | What it covers |
|---|---|
| [Config](config.md) | `SwanConfig`, the model configuration |
| [Grid](grid.md) | `SwanGrid`, the computational grid as a rompy grid |
| [Data and boundary interfaces](interfaces.md) | Input grids and boundary spectra from data sources, and the times set from the run |
| [Startup](startup.md) | `PROJECT`, `SET`, `MODE`, `COORDINATES` |
| [Computational grid](cgrid.md) | `CGRID`: regular, curvilinear and unstructured grids |
| [Input grids](inpgrid.md) | `INPGRID`, `READINP`, constant `WIND` and `ICE` |
| [Boundary and initial conditions](boundary.md) | `BOUNDSPEC`, `BOUNDNEST1/2/3`, `INITIAL` |
| [Physics](physics.md) | Generation, dissipation, nonlinear interactions and other processes |
| [Numerics](numerics.md) | `PROP`, `NUMERIC` |
| [Output](output.md) | Output locations, quantities and write commands |
| [Lockup](lockup.md) | `COMPUTE`, `HOTFILE`, `STOP` |
| [Command groups](groups.md) | The groups `SwanConfig` takes as one field |
| [Subcomponents](subcomponents.md) | Parts of commands shared by several components |
| [Base components](base.md) | Base classes of the components and subcomponents |
| [Types](types.md) | Enumerations |
| [Command index](commands.md) | Every SWAN command and the component that writes it |
