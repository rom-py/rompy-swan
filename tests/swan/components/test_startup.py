"""Test startup components."""
import pytest
import logging
from pydantic import ValidationError

from rompy.swan.components.startup import PROJECT, SET


def test_project():
    proj = PROJECT(
        name="Test project",
        nr="0001",
        title1="Title 1",
        title2="Title 2",
        title3="Title 3",
    )
    assert proj.render() == (
        "PROJECT name='Test project' nr='0001' "
        "title1='Title 1' title2='Title 2' title3='Title 3'"
    )


def test_project_no_titles():
    proj = PROJECT(
        name="Test project",
        nr="0001",
    )
    assert proj.render() == ("PROJECT name='Test project' nr='0001'")


def test_set():
    s = SET(direction_convention="nautical")
    assert s.render() == "SET NAUTICAL"