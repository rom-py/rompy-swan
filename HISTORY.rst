=======
History
=======

Relocatable Ocean Modelling in PYthon (rompy) is a modular Python library that
aims to streamline the setup, configuration, execution, and analysis of coastal
ocean models. Rompy combines templated model configuration with xarray-based
data handling and pydantic validation, enabling users to efficiently generate
model control files and input datasets for a variety of ocean and wave models.
The architecture centers on high-level execution control (`ModelRun`) and
flexible configuration objects, supporting both persistent scientific model
state and runtime backend selection. Rompy provides unified interfaces for
grids, data sources, boundary conditions, and spectra, with extensible plugin
support for new models and execution environments. Comprehensive documentation,
example Jupyter notebooks, and a robust logging/formatting framework make rompy
accessible for both research and operational workflows. Current model support
includes SWAN and SCHISM, with ongoing development for additional models and
cloud/HPC backends.

Key Features: - Modular architecture with clear separation of configuration and
execution logic - Templated, reproducible model configuration using pydantic
and xarray - Unified interfaces for grids, data, boundaries, and spectra -
Extensible plugin system for models, data sources, backends, and postprocessors
- Robust logging and formatting for consistent output and diagnostics - Example
  notebooks and comprehensive documentation for rapid onboarding - Support for
  local, Docker, and HPC execution backends

rompy is under active development—features, model support, and documentation
are continually evolving. Contributions and feedback are welcome!


********
Releases
********

Unreleased
__________

Bug Fixes
---------
* In stationary mode (``MODE STATIONARY``, SWAN's default when ``startup.mode`` is not set) the lockup now writes a plain ``COMPUTE`` and output components are written without times. SWAN rejected the times that were always written, so these runs failed. ``SwanConfig`` now also reports, when it is created, the combinations SWAN refuses in stationary mode: a nonstationary computation or series of computations, output times, and time-varying inputs from the data or boundary interfaces. A stationary computation at a given time is ``COMPUTE_STAT`` with ``MODE NONSTATIONARY``.
* Input grids with a single point along an axis (usually data coarser than the model grid) raise a clear error instead of writing ``nan`` into the ``INPGRID`` command.
* The data-driven ``BoundspecSide`` and ``BoundspecSegmentXY`` boundaries now write the ``BOUND SHAPESPEC`` command. Without it SWAN applied its default ``DSPR POWER`` to the directional spreading in the TPAR files, which is given in degrees.
* TPAR boundary files are no longer written with zeros where the boundary spectra are missing, for example when a boundary point is beyond the selection tolerance. An error explains the likely cause instead.
* ``BoundspecSegmentXY`` has its own ``model_type`` (``boundspecsegmentxy``) instead of sharing ``boundspecside`` with ``BoundspecSide``, and ``BoundaryInterface.kind`` is discriminated by ``model_type``, so YAML configurations load the intended class. YAML files that used ``boundspecside`` for a segment boundary must change it to ``boundspecsegmentxy``.
* Input grids other than the bottom (wind, currents, water level, ...) now write missing values as the declared exception value instead of ``nan``, write rows along the y axis whatever the dimension order of the dataset, and raise a clear error when fewer than two times are available.
* The exception value of input grids is now multiplied by ``fac``, as SWAN expects. With ``fac=-1`` (elevation data) missing points were previously read as 99 m deep water.
* ``NUMERIC`` now renders its ``csigma`` and ``setup`` options, which were silently dropped.
* ``SPEC1D`` renders ``SPEC1D`` instead of ``SPEC2D``; ``CURVILINEAR`` renders ``yexc`` instead of repeating ``xexc``; ``CSIGMA`` and ``OUTPUT_OPTIONS`` have their own ``model_type`` values (``csigma`` and ``output_options``).
* The ``OUTPUT`` group checks every write component's location, instead of stopping at the first one that uses a special name such as ``COMPGRID``.
* Removed a stray ``print`` of the physics options when ``PHYSICS.deactivate`` is set.
* Importing ``rompy_swan`` no longer reconfigures rompy's logging, which reset the log level set by the user (for example with ``rompy.logging.config.update(level="WARNING")``) to INFO.


0.11.1 (2026-07-27)
____________________

Bug Fixes
---------
* The ``POINTS_FILE`` component now renders the mandatory ``FILE`` keyword, i.e. ``POINTS 'sname' FILE 'fname'``, so SWAN correctly reads the output locations from file. Reported by `@JOHN8736 <https://github.com/JOHN8736>`_ (`#17 <https://github.com/rom-py/rompy-swan/issues/17>`_).


0.11.0 (2026-07-03)
____________________

New Features
------------
* The output time range can now start later than the simulation, allowing a spin-up period to be excluded from output files. A ``tbeg`` explicitly set in the ``times`` field of write components is preserved by the ``OutputInterface`` instead of being overwritten by the runtime start time, by `@benjaminleighton <https://github.com/benjaminleighton>`_ (`#16 <https://github.com/rom-py/rompy-swan/pull/16>`_).

Bug Fixes
---------
* Relaxed the maximum hotfile filename length in the ``HOTSINGLE`` and ``HOTMULTIPLE`` subcomponents from 36 to 80 characters, by `@rsoutelino <https://github.com/rsoutelino>`_ (`#15 <https://github.com/rom-py/rompy-swan/pull/15>`_).


0.10.0 (2026-04-15)
____________________

New Features
------------
* Added ``NEST`` component that couples ``NGRID`` and ``NESTOUT`` under a single ``sname``, enabling multiple nested grids to be defined via the ``nests`` field in the ``OUTPUT`` group (`#13 <https://github.com/rom-py/rompy-swan/pull/13>`_). Thanks to `@MireyaMMO <https://github.com/MireyaMMO>`_ for her first contribution!
* The ``OutputInterface`` now injects run-period times into ``NESTOUT`` components within ``NEST`` objects, consistent with other write components.

Deprecations
------------
* Defining ``NGRID`` and ``NESTOUT`` individually in the ``OUTPUT`` group is deprecated. Use the ``NEST`` component and the ``nests`` field instead. Legacy fields are still accepted and automatically migrated, but will be removed in a future version.


0.9.0 (2026-02-10)
___________________

New Features
------------
* Added support for controlling the output time interval independently of the run interval via the ``times`` field in write components (``BLOCK``, ``TABLE``, ``SPECOUT``).

Internal Changes
----------------
* Redesigned documentation with MkDocs, including new examples section and time control guide.
* Added ``pydantic-numpy`` as an explicit dependency (no longer bundled with ``rompy``).


0.8.0 (2026-01-13)
___________________

New Features
------------
* Added extra frequency-split partitioned parameters to BlockOptions Enum (`#10 <https://github.com/rom-py/rompy-swan/pull/10>`_). Thanks to `@rsoutelino <https://github.com/rsoutelino>`_ for his first contribution!

Internal Changes
----------------
* Migrated documentation from Sphinx to MkDocs.
* Added envyaml dependency for YAML configuration with environment variable support.
* Deprecated ``SwanConfigComponents`` in favor of ``SwanConfig``. The old class remains available for backward compatibility but will be removed in a future version.
* Removed legacy SwanConfig templates and objects.


0.5.0 (2025-07-13)
___________________

New Features
------------
* Improved logging for SCHISM model components.
* Added string formatting methods for SCHISM components.
* Added backend testing and execution scripts.
* Added backend config examples and quickstart test script.
* Added backend demo notebook and documentation.
* Added support for multiple include_modules in docker.
* Added docker backend test and setup.

Bug Fixes
---------
* Fixed backend demo notebook.
* Fixed merge issues and improved PyLibs import handling.
* Fixed mounting workspace in docker.
* Fixed issues from merge and removed redundant code.

Internal Changes
----------------
* Refactored backend approach using strong typing.
* Improved backend docs and tutorial.
* Consolidated documentation and removed legacy sections.
* Improved INPUT file diagnostics in Docker container.


0.4.0 (2025-07-10)
___________________

New Features
------------
* Refactored SCHISM boundary conditions, unified SCHISMDataTides and SCHISMDataOcean into SCHISMDataBoundaryConditions.
* Added support for pyTMD for tidal forcing.
* Added tidal database and updated yaml of tidal runs.
* Added boundary condition examples and documentation.
* Added plotting utilities and improved grid plotting.
* Added support for v5.12 vegetation model.
* Added MDT specification for TidalDataset for Z0.

Bug Fixes
---------
* Fixed duplicated subfolder for oceanum-atlas in database.json.
* Fixed test cases for pyTMD compatibility.
* Fixed decorators and case handling for tidal API.
* Fixed missing station.in file for tidal examples.
* Fixed case test with new tidal API.

Internal Changes
----------------
* Restructured SCHISM boundary condition naming.
* Overwrote pre-refactor config files with post-refactor versions.
* Cleaned up code and tests.
* Updated enum types and documentation.



0.3.0 (2023-03-29)
___________________

Major refactor: redefinition of the entire codebase using pydantic models.
Separation of concerns between runtime information and model configuration.
Added model_type field and pydantic basegrid.
Added methods to store and dump original inputs to RompyBaseModel.
Added json support to CLI.
Added iso timedelta for JSON serialization.
Added DataPoint object and timeseries-based sources.
Added validator for hotfiles against timestep.

Bug Fixes
---------
Fixed issue with create_model in older versions of pydantic.
Fixed validator of IDLA to fix serialization issue.
Fixed path definition in new test.
Fixed schism serialization issues.
Fixed bug in string output of regular grid for SWAN.

Internal Changes
----------------
Removed convenience imports from core.
Promoted appdirs dependency from schism to main list.
Reordered imports.
Refactored intake source to prevent recursion with dask.
Cleaned up debug messages and removed redundant code.

0.1.0 (2023-MM-DD)
___________________

Initial release of rompy with basic functionality for coastal ocean model configuration and execution.
Provided example Jupyter notebooks for setup, evaluation, and visualization.
Basic support for SWAN and SCHISM models.


.. _`CSIRO`: https://www.csiro.au/en/
.. _`Oceanum`: https://oceanum.science/
