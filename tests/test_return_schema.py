"""Config-driven output declarations and filesystem-backed evidence."""

import pytest
from rompy.core.responses import Artifact, ArtifactType

from rompy_swan.config import SwanConfig, SwanConfigComponents


@pytest.fixture
def config():
    return SwanConfig(
        cgrid={
            "model_type": "regular",
            "spectrum": {"mdc": 36, "flow": 0.04, "fhigh": 0.4},
            "grid": {
                "xp": 0,
                "yp": 0,
                "alp": 0,
                "xlen": 1,
                "ylen": 1,
                "mx": 10,
                "my": 10,
            },
        }
    )


def test_empty_output(config):
    assert config.expected_artifacts() == []


def test_configured_writes_not_input_locations(config):
    from rompy_swan.components.group import OUTPUT

    config.output = OUTPUT(
        points={"model_type": "points_file", "sname": "pts", "fname": "locations.txt"},
        block={
            "model_type": "blocks",
            "components": [
                {"sname": "COMPGRID", "fname": "./fields.nc", "output": ["hsign"]},
                {"sname": "COMPGRID", "fname": "fields.mat", "output": ["hsign"]},
            ],
        },
        table={"sname": "pts", "fname": "table.txt", "output": ["hsign"]},
        specout={"sname": "pts", "fname": "spectra.nc"},
    )
    artifacts = {a.path: a.artifact_type for a in config.expected_artifacts()}
    assert artifacts == {
        "fields.nc": ArtifactType.NETCDF,
        "fields.mat": ArtifactType.OTHER,
        "table.txt": ArtifactType.TEXT,
        "spectra.nc": ArtifactType.NETCDF,
    }


def test_nests(config):
    from rompy_swan.components.group import OUTPUT

    config.output = OUTPUT(
        nests=[
            {
                "sname": "child",
                "ngrid": {
                    "model_type": "ngrid",
                    "sname": "child",
                    "grid": {
                        "xp": 0,
                        "yp": 0,
                        "alp": 0,
                        "xlen": 1,
                        "ylen": 1,
                        "mx": 2,
                        "my": 2,
                    },
                },
                "nestout": {"sname": "child", "fname": "child.swn"},
            }
        ]
    )
    assert [a.path for a in config.expected_artifacts()] == ["child.swn"]


@pytest.mark.parametrize("mode", ["stat", "nonstat"])
def test_timestamped_hotfiles(config, mode):
    from rompy_swan.components.group import LOCKUP, STARTUP

    config.startup = STARTUP(mode={"kind": "nonstationary"})
    config.lockup = LOCKUP(
        compute={
            "model_type": mode,
            "times": {
                "model_type": "nonstationary",
                "tbeg": "2024-01-01T00:00:00",
                "tend": "2024-01-01T02:00:00",
                "delt": "PT1H",
            },
            "hotfile": {"fname": "hot.swn"},
            "hottimes": [1, -1],
        }
    )
    expected = config.expected_artifacts()
    assert [a.path for a in expected] == [
        "hot_20240101T010000.swn",
        "hot_20240101T020000.swn",
    ]
    assert all(a.artifact_type == ArtifactType.RESTART for a in expected)
    assert all(a.path in config.lockup.render() for a in expected)


def test_stationary_hotfile(config):
    from rompy_swan.components.group import LOCKUP

    config.lockup = LOCKUP(
        compute={"model_type": "compute", "hotfile": {"fname": "hot.swn"}}
    )
    artifacts = config.expected_artifacts()
    assert [(a.path, a.artifact_type) for a in artifacts] == [
        ("hot.swn", ArtifactType.RESTART)
    ]
    assert "hot.swn" in config.lockup.render()


def test_deprecated_config_inherits_contract():
    assert SwanConfigComponents.expected_artifacts is SwanConfig.expected_artifacts


def test_observed_evidence_excludes_missing_and_sidecars(config, tmp_path):
    from rompy_swan.components.group import OUTPUT

    config.output = OUTPUT(
        block={
            "model_type": "block",
            "sname": "COMPGRID",
            "fname": "missing.nc",
            "output": ["hsign"],
        }
    )
    (tmp_path / "actual.nc").write_bytes(b"data")
    (tmp_path / "run_result.json").write_text("{}")
    (tmp_path / ".rompy-postprocess").mkdir()
    (tmp_path / ".rompy-postprocess" / "hidden.txt").touch()
    with pytest.warns(UserWarning, match="missing.nc"):
        artifacts = config.validate_outputs(tmp_path)
    assert [(a.path, a.size_bytes) for a in artifacts] == [("actual.nc", 4)]
    assert Artifact.model_validate(artifacts[0].model_dump(mode="json")) == artifacts[0]


def test_core_run_preserves_missing_evidence_and_sidecar(config, tmp_path):
    from rompy.backends import LocalConfig
    from rompy.core.result_persistence import load_run_result
    from rompy.model import ModelRun

    from rompy_swan.components.group import OUTPUT

    config.output = OUTPUT(
        block={
            "model_type": "block",
            "sname": "COMPGRID",
            "fname": "missing.nc",
            "output": ["hsign"],
        }
    )
    run = ModelRun(
        run_id="schema-test",
        config=config,
        output_dir=str(tmp_path),
        period={"start": "2024-01-01", "end": "2024-01-02", "interval": "1h"},
    )
    workspace = tmp_path / run.run_id
    workspace.mkdir()
    # Exercise real generation/execution/persistence without requiring SWAN.
    with pytest.warns(UserWarning, match="missing.nc"):
        result = run.run(
            backend=LocalConfig(
                command="printf data > actual.nc",
                working_dir=workspace,
            )
        )
    assert result.success
    assert [a.path for a in result.expected_outputs] == ["missing.nc"]
    assert [a.path for a in result.missing_outputs] == ["missing.nc"]
    assert "missing.nc" not in {a.path for a in result.artifacts}
    assert "actual.nc" in {a.path for a in result.artifacts}
    persisted = load_run_result(workspace / "run_result.json")
    assert persisted.payload == result


def test_discovery_does_not_follow_escaping_symlinks(config, tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.nc"
    outside.write_bytes(b"not output")
    (tmp_path / "escape.nc").symlink_to(outside)
    assert config.validate_outputs(tmp_path) == []
