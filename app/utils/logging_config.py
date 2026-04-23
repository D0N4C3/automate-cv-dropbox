import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(level: str = "INFO") -> None:
    Path("logs").mkdir(exist_ok=True)
    root = logging.getLogger()
    root.setLevel(level.upper())

    if not root.handlers:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(LOG_FMT))

        file_handler = RotatingFileHandler("logs/app.log", maxBytes=2_000_000, backupCount=5)
        file_handler.setFormatter(logging.Formatter(LOG_FMT))

        root.addHandler(console)
        root.addHandler(file_handler)
