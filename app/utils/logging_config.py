import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_LOG_FILE = "logs.txt"


def setup_logging(level: str = "INFO") -> None:
    project_root = Path(__file__).resolve().parents[2]
    log_dir = Path(os.getenv("LOG_DIR", project_root / "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level.upper())

    formatter = logging.Formatter(LOG_FMT)

    has_console = any(isinstance(handler, logging.StreamHandler) for handler in root.handlers)
    if not has_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

    log_file = log_dir / DEFAULT_LOG_FILE
    has_file = any(
        isinstance(handler, RotatingFileHandler) and Path(getattr(handler, "baseFilename", "")) == log_file
        for handler in root.handlers
    )
    if not has_file:
        file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=10)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    root.info("Logging initialized at level=%s, file=%s", level.upper(), log_file)
