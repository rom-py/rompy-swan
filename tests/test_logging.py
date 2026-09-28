"""Test that importing rompy_swan keeps the user's logging settings."""

import importlib
import logging

from rompy.logging import config as logging_config


def test_import_keeps_log_level():
    logging_config.update(level="WARNING")
    import rompy_swan

    importlib.reload(rompy_swan)
    assert logging.getLogger().level == logging.WARNING
