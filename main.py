import logging

import app  # noqa: F401
from app.config import settings
from app.database import init_db
from app.services.sync_service import SyncService
from app.utils.logging_config import setup_logging


def run_sync() -> None:
    setup_logging(settings.log_level)
    init_db()
    logging.getLogger(__name__).info("Starting email sync job")
    SyncService().run()


if __name__ == "__main__":
    run_sync()
