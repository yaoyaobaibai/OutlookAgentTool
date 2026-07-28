# -*- coding: utf-8 -*-
"""Centralized logging setup for FormFiller.

Pattern matches PRPOAgent's _setup_ui_logging:
- Each launch creates a NEW timestamped log file (mode="w")
- Default log dir: %USERPROFILE%/FormFiller_logs/
- Format: %(asctime)s [%(levelname)s] %(name)s: %(message)s

Usage:
    from logging_setup import setup_logging, get_log_path
    logger, log_path = setup_logging()  # configure root logger + create log file
    logger.info("Some event happened")
"""

import logging
import os
from datetime import datetime


_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_logger = None
_log_path = None


def setup_logging(log_dir_path=None, level=logging.INFO):
    """Configure root logger with a FileHandler to a timestamped log file.

    Returns:
        tuple: (logger, log_path) — the root logger and the path to the log file
    """
    global _logger, _log_path

    if log_dir_path is None:
        log_dir_path = os.path.expandvars(r"%USERPROFILE%\FormFiller_logs")

    os.makedirs(log_dir_path, exist_ok=True)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir_path, f"log_{timestamp}.log")

    # Get root logger
    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing FileHandlers to avoid duplicates on re-setup
    for h in list(root.handlers):
        if isinstance(h, logging.FileHandler):
            root.removeHandler(h)

    # Add new FileHandler (mode="w" truncates, fresh file per launch)
    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(_formatter)
    root.addHandler(file_handler)

    _logger = root
    _log_path = log_path

    root.info("=" * 60)
    root.info(f"FormFiller started at {datetime.now().isoformat()}")
    root.info(f"Log file: {log_path}")
    root.info("=" * 60)

    return root, log_path


def get_log_path():
    """Return the path to the current log file (None if setup_logging not yet called)."""
    return _log_path
