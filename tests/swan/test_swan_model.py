"""Test swan_config class."""
import yaml
import pytest
import logging
from pathlib import Path

from rompy.core.model import BaseModel
from rompy.swan.config import SwanConfigPydantic as SwanConfig


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


@pytest.fixture(scope="module")
def config():
    yield yaml.load((HERE / "swan_model.yml").read_text(), Loader=yaml.Loader)


def test_swan_model(tmpdir, config):
    config = SwanConfig(
        project=config["project"],
        set=config["set"],
        mode=config["mode"],
        cgrid=config["cgrid"],
        inpgrid=config["inpgrid"],
        boundary=config["boundary"],
        initial=config["initial"],
    )
    model = BaseModel(
        run_id="test",
        output_dir=str(tmpdir),
        config=config,
        template="/source/csiro/rompy/rompy/templates/swan2",
    )
    # import ipdb; ipdb.set_trace()
    model.generate()
