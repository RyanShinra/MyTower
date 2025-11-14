# game/logger.py
import datetime
import logging
import os
from typing import Any, cast

# Define log levels with descriptive names
TRACE = 5  # Even more detailed than DEBUG
DEBUG = logging.DEBUG  # Detailed debug information
INFO = logging.INFO  # Confirmation that things are working as expected
WARNING = logging.WARNING  # Indication that something unexpected happened
ERROR = logging.ERROR  # Error that prevented something from working
CRITICAL = logging.CRITICAL  # A serious error that might prevent the program from continuing

# Register the TRACE level with the logging system
logging.addLevelName(TRACE, "TRACE")


class MyTowerLogger(logging.Logger):
    """Custom logger class with TRACE level support."""

    def trace(self, msg: object, *args: Any, **kwargs: Any) -> None:  # type: ignore[explicit-any]
        """
        Log a message with severity 'TRACE'.

        Args:
            msg: The message to log
            args: Arguments to merge into msg using string formatting
            kwargs: Additional arguments to pass to the logging method
        """
        if self.isEnabledFor(TRACE):
            self._log(TRACE, msg, args, **kwargs)

    def get_level_name(self, level: int) -> str:
        """Get the string name of a log level."""
        return logging.getLevelName(level)

# Register our custom logger class with the logging system BEFORE creating any loggers
logging.setLoggerClass(MyTowerLogger)


def setup_logger(
    name: str = "mytower",
    level: int = logging.INFO,
    log_file: str | None = None,
    console: bool = True,
    file_level: int | None = None,
    console_level: int | None = None,
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
        "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    simple_formatter = logging.Formatter("%(asctime)s.%(msecs)03d | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S")

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

# # Create a root logger for the game
# root_logger = setup_logger(
#     name="mytower",
#     level=TRACE,  # Capture all logs at the logger level
#     log_file=f"logs/mytower_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
#     file_level=TRACE,  # Write all levels to file
#     console_level=DEBUG,  # Only show DEBUG and higher in console
# )

# Create function to get module-specific loggers
# def get_logger(module_name: str) -> MyTowerLogger:
#     """Get a logger for a specific module."""
#     # Prepend mytower to create a hierarchy
#     return cast(MyTowerLogger, logging.getLogger(f"mytower.{module_name}"))


# Create a LoggerProvider:
class LoggerProvider:
    """Provides loggers for different modules, sharing a root logger."""

    def __init__(
        self,
        root_logger: MyTowerLogger | None = None,
        log_level: int = logging.INFO,
        log_file: str | None = None,
        file_log_level: int = TRACE,
    ) -> None:
        if root_logger:
            self._root_logger = root_logger
        else:
            file_name_part, file_ext_part = os.path.splitext(log_file) if log_file else ("mytower", ".log")
            date_string: str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

            # Pass log_level to setup_logger
            self._root_logger: logging.Logger = setup_logger(
                name="mytower",
                level=log_level,
                log_file=(
                    f"{file_name_part}_{date_string}{file_ext_part}"
                    if log_file else None
                ),
                file_level=file_log_level,  # Default Trace log everything to file
                console_level=log_level,  # Use specified level for console
            )
        self._loggers: dict[str, MyTowerLogger] = {}

    def get_logger(self, module_name: str) -> MyTowerLogger:
        if module_name not in self._loggers:
            self._loggers[module_name] = cast(MyTowerLogger, logging.getLogger(f"mytower.{module_name}"))
        return self._loggers[module_name]
