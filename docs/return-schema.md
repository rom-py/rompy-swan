# Return-schema reference

`SwanConfig.expected_artifacts()` returns core `Artifact` objects for configured
BLOCK/BLOCKS, TABLE, SPECOUT, NESTOUT/NEST and TEST writes. Input filenames in
POINTS_FILE and NGRID are not output declarations. Duplicate paths are collapsed.
NetCDF outputs are classified as `NETCDF`, MATLAB outputs as `OTHER`, other SWAN
writes as `TEXT`, and timestamped HOTFILE writes as `RESTART`. Hotfile names use
the same `hottimes` and suffix expansion as the rendered COMPUTE commands.
`SwanConfigComponents` inherits this contract.

`validate_outputs(workspace)` returns only existing files, with byte sizes. It
warns for absent declarations without reporting them as observed. Core can then
populate `expected_outputs` and `missing_outputs` in `ModelRun.run()` results.
Discovery also includes input/control files and auxiliary outputs; it excludes
core result sidecars, `.rompy-postprocess` and symlinks escaping the workspace.
Declarations require normalized workspace-relative paths (a leading `./` is
normalized); absolute paths and parent traversal are rejected by core.

Expected hotfiles follow serial SWAN naming. MPI-partitioned hotfiles are
additionally discovered, but processor count is backend information unavailable
to the config. Override expectations for MPI hotfile completeness checks.
Presence checks do not validate NetCDF contents or scientific correctness.
