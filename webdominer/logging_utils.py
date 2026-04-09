from __future__ import annotations

import logging
from logging import Logger

from .settings import Settings


def configure_logging(settings: Settings) -> None:
    """
    Configure root logging for both console and file output.

    Safe to call multiple times; existing handlers will be replaced.
    """
    settings.ensure_directories()

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicate logs.
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    file_handler = logging.FileHandler(settings.log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Keep project logs visible at the configured level.
    logging.getLogger("webdominer").setLevel(log_level)

    # Reduce noisy third-party loggers.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("keybert").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logging.getLogger("primp").setLevel(logging.WARNING)
    logging.getLogger("ddgs").setLevel(logging.WARNING)
    logging.getLogger("ddgs.ddgs").setLevel(logging.WARNING)

    logging.getLogger("trafilatura").setLevel(logging.WARNING)
    logging.getLogger("trafilatura.core").setLevel(logging.ERROR)
    logging.getLogger("trafilatura.metadata").setLevel(logging.ERROR)
    logging.getLogger("trafilatura.utils").setLevel(logging.ERROR)


def get_logger(name: str) -> Logger:
    """Return a logger with the provided module name."""
    return logging.getLogger(name)