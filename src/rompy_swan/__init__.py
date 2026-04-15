"""
SWAN Module for ROMPY

This module provides interfaces and utilities for working with the SWAN
(Simulating WAves Nearshore) model within the ROMPY framework.
"""

__version__ = "0.9.0"


from rompy.logging import LoggingConfig, get_logger

logger = get_logger(__name__)

# Configure logging for the SWAN module
logging_config = LoggingConfig()
logging_config.configure_logging()

# Log module initialization
logger.debug("SWAN module initialised")
