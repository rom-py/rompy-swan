"""
SWAN Module for ROMPY

This module provides interfaces and utilities for working with the SWAN
(Simulating WAves Nearshore) model within the ROMPY framework.
"""

__version__ = "0.11.1"


from rompy.logging import get_logger

# Logging is configured by rompy (rompy.logging.config), not on import, so that the
# user's settings are kept
logger = get_logger(__name__)
