# Contributing

Contributions are welcome: bug reports and ideas as [GitHub issues](https://github.com/rom-py/rompy-swan/issues), and changes as pull requests.

## Development setup

```bash
git clone https://github.com/rom-py/rompy-swan.git
cd rompy-swan
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Tests and style

```bash
pytest                    # the test suite; downloads the test data on first run
black --check src tests   # formatting, also run by the pre-commit hook
```

The test data (`tests/data`) is downloaded from [rompy-test-data](https://github.com/rom-py/rompy-test-data) the first time the tests run. Test what each component renders, each validator in both directions (accepted and rejected), and the files a data or boundary interface writes.

## Adding a SWAN command

Each component is one SWAN command (see [How rompy-swan works](../user-guide/how-it-works.md)). When adding one:

- **Put it where SWAN's manual groups it:** startup, computational grid, input grids, boundary, physics, numerics, output or lockup, in `src/rompy_swan/components/`. Parts shared by several commands go in `src/rompy_swan/subcomponents/`.
- **Name the class after the command** (`GEN3`, `BOUNDSPEC`) and give it a `model_type` literal with the lower- and upper-case name, so it can be selected in YAML.
- **Name the fields after the command's options** in the SWAN manual, and describe each with SWAN's default: `description="... (SWAN default: 0.5)"`. Use `ge`, `le`, `Literal` and enums for the valid values.
- **Implement `cmd()`** to return the command line, writing only the options that are set. `render()` splits long lines with SWAN's continuation character.
- **Use a discriminated union for a choice between variants**, such as the source term packages of `GEN3`, so only valid combinations can be built.
- **Render exactly the command.** Components do not change other components. Settings that depend on each other are checked by a validator on the group or on `SwanConfig`, which raises an error that says what to use instead.
- **Start the docstring with the command syntax** from the SWAN manual in a `text` code block, then a short description and an `Examples` section. The [command index](../reference/commands.md) is built from the syntax block, so the first word must be the SWAN command.

````python
class MYCMD(BaseComponent):
    """Short description of the command.

    ```text
    MYCMD [option]
    ```

    What the command does, in SWAN's terms.

    Examples
    --------
    ```python exec="on" source="above" result="text" session="mymodule-mycmd"
    from rompy_swan.components.mymodule import MYCMD
    print(MYCMD(option=1.0).render())
    ```
    """

    model_type: Literal["mycmd", "MYCMD"] = Field(
        default="mycmd", description="Model type discriminator"
    )
    option: Optional[float] = Field(
        default=None, description="What it sets (SWAN default: 1.0)", ge=0.0
    )

    def cmd(self) -> str:
        repr = "MYCMD"
        if self.option is not None:
            repr += f" option={self.option}"
        return repr
````

## Documentation

The docs are built with [ProperDocs](https://github.com/ProperDocs/properdocs) (a maintained fork of MkDocs 1.6), Material and mkdocstrings, using the shared configuration from [rompy-docs](https://github.com/rom-py/rompy-docs):

```bash
pip install -e ".[docs,test]"
python -c "import tests.conftest"           # download the example data into tests/data
properdocs serve -f mkdocs.yml              # live preview
properdocs build --strict -f mkdocs.yml     # what CI runs
rompy-docs check -f mkdocs.yml              # compare with the shared configuration
```

- **The reference is generated** from the docstrings and field descriptions, and lists the fields each class inherits from rompy.
- **Examples in docstrings and pages run when the docs are built.** Write them as markdown-exec blocks, as above; a failing example fails the strict build. Use a plain `python` block only for examples that need SWAN or remote data.
- **Link classes** with `` [`BOUNDSPEC`][rompy_swan.components.boundary.BOUNDSPEC] ``. rompy classes resolve to the rompy site.
- **Notebooks** live in [rompy-notebooks](https://github.com/rom-py/rompy-notebooks). The Tutorial and Examples pages list them from the inventory that site publishes.
- To build against an unpublished rompy site, set `ROMPY_INVENTORY` to its `objects.inv` (a URL, or `file://` path).

## Pull requests

1. Create a branch from `main`.
2. Make the change, with tests and docs.
3. Run the tests and the strict docs build.
4. Add the change to the Unreleased section of [`HISTORY.rst`](https://github.com/rom-py/rompy-swan/blob/main/HISTORY.rst), under Breaking Changes, New Features or Bug Fixes.
5. Open a pull request.

## Releases

The version is managed with [tbump](https://github.com/dmerejkowsky/tbump): `tbump <new_version>` updates `src/rompy_swan/__init__.py`, commits and tags `v<new_version>`. Move the Unreleased section of `HISTORY.rst` to the new version first. Publishing a GitHub release for the tag publishes the package on PyPI.
