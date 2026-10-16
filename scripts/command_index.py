"""Generate the SWAN command index for the docs (run by markdown-exec).

Every SWAN command rompy-swan can write, with the component that writes it. Each
component's docstring starts with the command syntax in a ```text block, whose
first word is the SWAN command, so the index is built from the code.
"""

from __future__ import annotations

import importlib
import inspect
import re

from rompy_swan.components.base import BaseComponent

# Reference page and SwanConfig field for each components module, in INPUT file order.
SECTIONS = [
    ("startup", "Startup", "startup"),
    ("cgrid", "Computational grid", "cgrid"),
    ("inpgrid", "Input grids", "inpgrid, forcing"),
    ("boundary", "Boundary and initial conditions", "boundary, initial"),
    ("physics", "Physics", "physics"),
    ("numerics", "Numerics", "prop, numeric"),
    ("output", "Output", "output"),
    ("lockup", "Lockup", "lockup"),
]

SYNTAX = re.compile(r"```text\n\s*(\S+)")


def _summary(doc: str) -> str:
    return doc.strip().splitlines()[0].rstrip(".").replace("|", "\\|") if doc.strip() else ""


def _components(module_name: str) -> list[tuple[str, str, str]]:
    """(command, class path, summary) for the components defined in a module."""
    module = importlib.import_module(f"rompy_swan.components.{module_name}")
    rows = []
    for name, cls in vars(module).items():
        if not (
            isinstance(cls, type)
            and issubclass(cls, BaseComponent)
            and cls.__module__ == module.__name__
        ):
            continue
        doc = inspect.getdoc(cls) or ""
        match = SYNTAX.search(doc)
        if match:
            rows.append((match.group(1), f"{module.__name__}.{name}", _summary(doc)))
    return rows


def command_index() -> str:
    """Markdown tables of the SWAN commands, one per section of the command file."""
    out = []
    for module_name, title, field in SECTIONS:
        out.append(f"## {title}\n")
        out.append(f"Set in `SwanConfig.{field.replace(', ', '` and `SwanConfig.')}`. "
                   f"See the [{title.lower()} reference]({module_name}.md).\n")
        out.append("| SWAN command | Component | Description |")
        out.append("|---|---|---|")
        for command, path, summary in sorted(_components(module_name), key=lambda r: (r[0], r[1])):
            out.append(f"| `{command}` | [`{path.rsplit('.', 1)[1]}`][{path}] | {summary} |")
        out.append("")
    return "\n".join(out)
