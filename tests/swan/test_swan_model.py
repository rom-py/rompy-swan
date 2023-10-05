"""Test swan_config class."""
import logging
from pathlib import Path
import pytest
import yaml

from rompy.model import ModelRun
from rompy.swan.config import SwanConfigComponents


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


@pytest.fixture(scope="module")
def config_dict():
    yield yaml.load((HERE / "swan_model.yml").read_text(), Loader=yaml.Loader)


def test_swan_model(tmpdir, config_dict):
    config = SwanConfigComponents(
        template=str(HERE / "../../rompy/templates/swancomp"),
        startup=config_dict["startup"],
        # cgrid=config_dict["cgrid"],
        # inpgrid=config_dict["inpgrid"],
        # boundary=config_dict["boundary"],
        initial=config_dict["initial"],
        physics=config_dict["physics"],
        prop=config_dict["prop"],
        numeric=config_dict["numeric"],
        output=config_dict["output"],
        lockup=config_dict["lockup"],
    )
    model = ModelRun(
        run_id="test",
        output_dir=str(tmpdir),
        config=config,
    )
    model.generate()
