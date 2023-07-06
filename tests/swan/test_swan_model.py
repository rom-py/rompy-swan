"""Test swan_config class."""
import logging
from pathlib import Path
from typing import Literal
from pydantic import Field
import pytest
import yaml

from rompy.model import ModelRun
from rompy.swan.config import SwanConfigComponents as SwanConfig
from rompy.swan.subcomponents.physics import SourceTerms


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


@pytest.fixture(scope="module")
def config_dict():
    yield yaml.load((HERE / "swan_model.yml").read_text(), Loader=yaml.Loader)


def test_swan_model(tmpdir, config_dict):
    config = SwanConfig(
        template=str(HERE / "../../rompy/templates/swancomp"),
        project=config_dict["project"],
        set=config_dict["set"],
        mode=config_dict["mode"],
        coordinates=config_dict["coordinates"],
        cgrid=config_dict["cgrid"],
        inpgrid=config_dict["inpgrid"],
        boundary=config_dict["boundary"],
        initial=config_dict["initial"],
        physics=config_dict["physics"],
    )
    model = ModelRun(
        run_id="test",
        output_dir=str(tmpdir),
        config=config,
    )
    model.generate()
