"""
Logging utilities for SpotifyScraper.

This module provides functions for configuring logging in the SpotifyScraper package,
with support for different log levels, file logging, and custom formatters.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union, Dict, Any


def configure_logging(
    level: Union[str, int] = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    format_string: Optional[str] = None,
    date_format: str = "%Y-%m-%d %H:%M:%S",
    log_to_console: bool = True,
) -> logging.Logger:
    """
    Configure logging for SpotifyScraper.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (optional)
        format_string: Log format string (optional)
        date_format: Date format for log entries (default: %Y-%m-%d %H:%M:%S)
        log_to_console: Whether to log to console (default: True)
        
    Returns:
        Configured logger
    """
    # Get the root logger for spotify_scraper
    logger = logging.getLogger("spotify_scraper")
    
    # Convert string level to numeric level if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # Set logger level
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicate logs
    logger.handlers = []
    
    # Define log format
    if not format_string:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string, datefmt=date_format)
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log file is provided
    if log_file:
        # Create directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent log propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Module name
        
    Returns:
        Logger instance
    """
    # Create a logger with the full name
    full_name = f"spotify_scraper.{name}"
    return logging.getLogger(full_name)


class LoggingContext:
    """
    Context manager for temporarily changing logging level.
    
    Usage:
        with LoggingContext('spotify_scraper', logging.DEBUG):
            # Code that should generate debug logs
    """
    
    def __init__(self, logger_name: str, level: Union[str, int]):
        """
        Initialize the context manager.
        
        Args:
            logger_name: Logger name
            level: Temporary logging level
        """
        self.logger = logging.getLogger(logger_name)
        self.level = level
        self.old_level = self.logger.level
    
    def __enter__(self) -> logging.Logger:
        """
        Set the temporary logging level.
        
        Returns:
            Logger instance
        """
        # Convert string level to numeric level if needed
        if isinstance(self.level, str):
            self.level = getattr(logging, self.level.upper(), logging.INFO)
        
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Restore the original logging level.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.logger.setLevel(self.old_level)
