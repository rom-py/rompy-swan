"""Test swan_config class."""
import logging
from pathlib import Path
import pytest
import os
from envyaml import EnvYAML

from rompy.model import ModelRun
from rompy.swan.config import SwanConfigComponents


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent

os.environ["ROMPY_PATH"] = str(HERE.parent.parent)


@pytest.fixture(scope="module")
def config_dict():
    yield EnvYAML(HERE / "swan_model.yml")


def test_swan_model(tmpdir, config_dict):
    config = SwanConfigComponents(
        template=str(HERE / "../../rompy/templates/swancomp"),
        startup=config_dict["startup"],
        grid=config_dict["grid"],
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
