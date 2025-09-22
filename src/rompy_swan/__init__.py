__version__ = "0.6.0"
"""
SWAN Module for ROMPY

This module provides interfaces and utilities for working with the SWAN
(Simulating WAves Nearshore) model within the ROMPY framework.
"""
from rompy.logging import LoggingConfig, get_logger

logger = get_logger(__name__)

# Configure logging for the SWAN module
logging_config = LoggingConfig()
logging_config.configure_logging()

# Log module initialization
logger.debug("SWAN module initialised")
