"""
Logging setup for PHYFlow framework.
Configures structured console logging and optional file logging per run.
"""

import logging
from pathlib import Path
from typing import Optional


def setup_logger(name: str = "phyflow", log_file: Optional[Path] = None, level: int = logging.INFO) -> logging.Logger:
    """Configures structured logger with console output and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
