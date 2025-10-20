# SWAN

TODO: Ensure the `model_type` is shown next to each class in the autosummaries.

TODO: Fix broken links to classes and modules.

## Grid

::: rompy_swan.grid.SwanGrid

## Data

::: rompy_swan.data.SwanDataGrid
::: rompy_swan.boundary.Boundnest1

## Components

SWAN command instructions are described in Rompy by a set of pydantic models defined as
`components`. Each component defines a full command instruction such as `PROJECT`,
`CGRID`, `GEN3`, NUMERIC, etc. Inputs to the components may include other pydantic
models called `subcomponents` to handle more complex arguments.

Components are subclasses of `rompy_swan.components.base.BaseComponent`.
The base component class implements the following attribues:

* The **model_type** field that should be overwritten in each component subclass. The
  `model_type` field is defined as a `Literal` type and is used to discriminate the
  exact components to use in fields defined by a `Union` type of two or more components
  in a declarative framework (i.e., instantiating with a dict from yaml or json file).

* The **cmd()** method that must be overwritten in each component subclass. The `cmd()`
  method should return either a string or a list of strings to fully define a SWAN
  command line instruction. A list of strings defines multiple command line
  instructions that are executed in sequence such as the INPGRID/READGRID components.

* The **render()** method that constructs the command line instruction from the content
  returned from the `cmd()` method. The `render()` method is typically called inside
  the `__call__` method of the config class to construct the specific command line
  instruction from that component, taking care of maximum line size, line break and
  line continuation.

Components are defined within the `rompy_swan.components` subpackage and
render an entire SWAN command line specification. The following modules are available:

* [Startup Components](components/startup.md)
* [CGRID Components](components/cgrid.md)
* [INPGRID Components](components/inpgrid.md)
* [Boundary Components](components/boundary.md)
* [Physics Components](components/physics.md)
* [Numerics Components](components/numerics.md)
* [Output Components](components/output.md)
* [Lockup Components](components/lockup.md)
* [Group Components](components/group.md)

## Subcomponents

Subcomponents are defined within the `rompy_swan.subcomponents` subpackage
and render part of a SWAN command line specification. They typically define specific
arguments to one or more component. The following modules are available:

* [Base Subcomponents](subcomponents/base.md)
* [Startup Subcomponents](subcomponents/startup.md)
* [Spectrum Subcomponents](subcomponents/spectrum.md)
* [Time Subcomponents](subcomponents/time.md)
* [CGRID Subcomponents](subcomponents/cgrid.md)
* [READGRID Subcomponents](subcomponents/readgrid.md)
* [Boundary Subcomponents](subcomponents/boundary.md)
* [Physics Subcomponents](subcomponents/physics.md)
* [Numerics Subcomponents](subcomponents/numerics.md)
* [Output Subcomponents](subcomponents/output.md)

## Interface

Interface classes provide an interface between swan components and higher level objects
such as `TimeRange`, `Data` and `Grid` objects. They are used inside the `__call__`
method of the config classes to pass instances of these objects to the appropriate
components and define consistent parameters to the config after instantiating them.

::: rompy_swan.interface.DataInterface
::: rompy_swan.interface.BoundaryInterface
::: rompy_swan.interface.OutputInterface
::: rompy_swan.interface.LockupInterface

## Types

SWAN types provide valid values for a specific SWAN command line argument.

* [Types Reference](reference/types.md)

[Link: Literal](https://docs.python.org/3/library/typing.html#typing.Literal)