# game/logger.py
import logging
import os
from datetime import datetime
# from typing import Optional, Dict, Any
from typing import Optional

# Define log levels with descriptive names
DEBUG = logging.DEBUG       # Detailed debug information
INFO = logging.INFO         # Confirmation that things are working as expected
WARNING = logging.WARNING   # Indication that something unexpected happened
ERROR = logging.ERROR       # Error that prevented something from working
CRITICAL = logging.CRITICAL # A serious error that might prevent the program from continuing

def setup_logger(
    name: str = "mytower",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    file_level: Optional[int] = None,
    console_level: Optional[int] = None
) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers.
    
    Args:
        name: Logger name (typically module name)
        level: Overall logger level
        log_file: Optional path to log file
        console: Whether to log to console
        file_level: Logging level for file handler (defaults to level)
        console_level: Logging level for console handler (defaults to level)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Don't propagate to parent loggers
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Add console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level or level)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_level or level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create a root logger for the game
root_logger = setup_logger(
    name="mytower",
    level=logging.DEBUG,
    log_file=f"logs/mytower_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    file_level=logging.DEBUG
)

# Create function to get module-specific loggers
def get_logger(module_name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    # Prepend mytower to create a hierarchy
    return logging.getLogger(f"mytower.{module_name}")