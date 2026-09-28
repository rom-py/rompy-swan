"""Test that importing rompy_swan keeps the user's logging settings."""

import importlib

from rompy.logging import LoggingConfig


def test_import_does_not_configure_logging(monkeypatch):
    calls = []
    monkeypatch.setattr(
        LoggingConfig, "configure_logging", lambda self: calls.append(1)
    )
    import rompy_swan

    importlib.reload(rompy_swan)
    assert calls == []
