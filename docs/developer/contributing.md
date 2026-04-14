# Contributing

Contributions to rompy-swan are welcome! This guide covers how to set up a development environment and contribute to the project.

## Development Setup

### Clone the Repository

```bash
git clone https://github.com/rom-py/rompy-swan.git
cd rompy-swan
```

### Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### Install in Development Mode

```bash
pip install -e ".[dev]"
```

### Install Pre-commit Hooks

```bash
pre-commit install
```

## Running Tests

```bash
pytest tests/
```

With coverage:

```bash
pytest tests/ --cov=rompy_swan --cov-report=html
```

## Code Style

Rompy-swan uses:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all checks:

```bash
pre-commit run --all-files
```

## Documentation

### Build Docs Locally

```bash
pip install -e ".[docs]"
mkdocs serve
```

Then open http://localhost:8000 in your browser.

### Writing Documentation

- Use Markdown for all documentation
- Follow the existing structure in `docs/`
- Add docstrings to all public classes and functions
- Include examples in docstrings

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

## Adding New Components

When adding new SWAN components:

1. Create the component class in the appropriate module under `rompy_swan/components/`
2. Inherit from `BaseComponent`
3. Implement the `cmd()` method
4. Add the `model_type` field as a `Literal`
5. Add tests in `tests/`
6. Add documentation in `docs/components/`

Example:

```python
from typing import Literal
from pydantic import Field
from rompy_swan.components.base import BaseComponent

class MY_COMMAND(BaseComponent):
    """My new SWAN command.
    
    This command does something useful.
    
    Examples
    --------
    >>> cmd = MY_COMMAND(param=1.0)
    >>> print(cmd.render())
    MY_COMMAND param=1.0
    
    """
    
    model_type: Literal["my_command"] = Field(
        default="my_command",
        description="Model type discriminator",
    )
    param: float = Field(
        default=1.0,
        description="Parameter description",
        ge=0.0,
    )
    
    def cmd(self) -> str:
        return f"MY_COMMAND param={self.param}"
```

## Reporting Issues

Please report issues on the [GitHub issue tracker](https://github.com/rom-py/rompy-swan/issues).

Include:

- Python version
- rompy-swan version
- Minimal reproducible example
- Expected vs actual behavior

## Questions

For questions, please use [GitHub Discussions](https://github.com/rom-py/rompy-swan/discussions).
