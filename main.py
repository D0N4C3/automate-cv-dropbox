import logging

import app  # noqa: F401
from app.config import settings
from app.database import init_db
from app.services.sync_service import SyncService
from app.utils.logging_config import setup_logging


def run_sync() -> None:
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting email sync job")
    try:
        init_db()
        SyncService().run()
        logger.info("Email sync job completed")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Email sync job failed: %s", exc)
        raise


if __name__ == "__main__":
    run_sync()
