"""Filesystem evidence for the canonical rompy return schema."""

import warnings
from pathlib import Path

from rompy.core.responses import Artifact, ArtifactType

_RESERVED = {"generate_result.json", "run_result.json", "postprocess_result.json"}
_TYPES = {
    ".nc": ArtifactType.NETCDF,
    ".yaml": ArtifactType.YAML,
    ".yml": ArtifactType.YAML,
    ".txt": ArtifactType.TEXT,
    ".swn": ArtifactType.TEXT,
    ".nml": ArtifactType.TEXT,
    ".log": ArtifactType.TEXT,
    ".out": ArtifactType.TEXT,
    **dict.fromkeys((".png", ".jpg", ".jpeg", ".svg", ".pdf"), ArtifactType.PLOT),
}


def discover_artifacts(
    output_dir: Path | str, expected: list[Artifact]
) -> list[Artifact]:
    """Return only existing files, preserving configured types and descriptions.

    Like core's generic discovery, include controls and auxiliary files as well
    as model outputs. Never use a missing declaration as observed evidence.
    Sidecars, internal postprocessing files and escaping symlinks are excluded.
    """
    root = Path(output_dir).resolve()
    declared = {item.path: item for item in expected}
    observed = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.name in _RESERVED or ".rompy-postprocess" in relative.parts:
            continue
        if not path.resolve().is_relative_to(root) or not path.is_file():
            continue
        name = relative.as_posix()
        artifact = declared.get(name)
        if artifact is None:
            artifact_type = _TYPES.get(path.suffix.lower(), ArtifactType.OTHER)
            if any(
                item.artifact_type == ArtifactType.RESTART
                and name.startswith(item.path + "-")
                for item in expected
            ):
                artifact_type = ArtifactType.RESTART
            artifact = Artifact(path=name, artifact_type=artifact_type)
        observed[name] = artifact.model_copy(update={"size_bytes": path.stat().st_size})
    for item in expected:
        if item.path not in observed:
            warnings.warn(
                f"Expected artifact not found: {item.path}", UserWarning, stacklevel=2
            )
    return list(observed.values())
