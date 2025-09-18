"""Test swan_config class."""

import os
from pathlib import Path

import pytest
from envyaml import EnvYAML

# Import test utilities
from test_utils.logging import get_test_logger

from rompy.core.source import SourceIntake
from rompy.model import ModelRun
from rompy_swan.boundary import Boundnest1
from rompy_swan.config import SwanConfig
from rompy_swan.interface import BoundaryInterface

# Initialize logger
logger = get_test_logger(__name__)

HERE = Path(__file__).parent

os.environ["ROMPY_PATH"] = str(HERE.parent)


@pytest.fixture(scope="module")
def config_dict():
    yield EnvYAML(HERE / "swan_model.yml")


def test_swan_model(tmpdir, config_dict):
    config = SwanConfig(
        startup=config_dict["startup"],
        cgrid=config_dict["cgrid"],
        inpgrid=config_dict["inpgrid"],
        boundary=config_dict["boundary"],
        initial=config_dict["initial"],
        physics=config_dict["physics"],
        prop=config_dict["prop"],
        numeric=config_dict["numeric"],
        output=config_dict["output"],
        lockup=config_dict["lockup"],
    )
    model = ModelRun(
        run_id="test",
        period=dict(start="20230101T00", duration="12h", interval="1h"),
        output_dir=str(tmpdir),
        config=config,
    )
    model.generate()


def test_swan_model_boundary(tmpdir, config_dict):
    config = SwanConfig(
        startup=config_dict["startup"],
        cgrid=config_dict["cgrid"],
        inpgrid=config_dict["inpgrid"],
        boundary=BoundaryInterface(
            kind=Boundnest1(
                id="wave_forcing",
                source=SourceIntake(
                    dataset_id="ausspec", catalog_uri=HERE / "data/catalog.yaml"
                ),
            )
        ),
        initial=config_dict["initial"],
        physics=config_dict["physics"],
        prop=config_dict["prop"],
        numeric=config_dict["numeric"],
        output=config_dict["output"],
        lockup=config_dict["lockup"],
    )
    model = ModelRun(
        run_id="test",
        period=dict(start="20230101T00", duration="12h", interval="1h"),
        output_dir=str(tmpdir),
        config=config,
    )
    model.generate()
