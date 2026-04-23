import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path

from app.config import settings
from app.services.sync_service import SyncService

logger = logging.getLogger(__name__)


class HourlySyncScheduler:
    def __init__(self) -> None:
        self.interval_seconds = max(settings.sync_interval_minutes, 1) * 60
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._running = False
        self._lock_file = settings.scheduler_lock_file

    def start(self) -> None:
        if self._running:
            logger.info("Hourly sync scheduler already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="hourly-sync-scheduler")
        self._thread.start()
        logger.info("Hourly sync scheduler started interval=%s minutes", settings.sync_interval_minutes)

    def _run_loop(self) -> None:
        while self._running:
            stop_at = datetime.utcnow() + timedelta(seconds=self.interval_seconds)
            while self._running and datetime.utcnow() < stop_at:
                threading.Event().wait(timeout=1)
            if self._running:
                self._run_once(trigger="scheduler")

    def run_now(self) -> None:
        self._run_once(trigger="manual")

    def _run_once(self, trigger: str) -> None:
        if not self._lock.acquire(blocking=False):
            logger.info("Skipping %s sync trigger because another sync is currently running", trigger)
            return

        try:
            lock_path = Path(self._lock_file)
            lock_path.parent.mkdir(parents=True, exist_ok=True)

            with lock_path.open("a+", encoding="utf-8") as lock_handle:
                try:
                    import fcntl

                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    logger.info(
                        "Skipping %s sync trigger because scheduler lock is held by another process lock_file=%s",
                        trigger,
                        self._lock_file,
                    )
                    return

                logger.info("Starting %s sync trigger", trigger)
                SyncService().run()
                logger.info("Finished %s sync trigger", trigger)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Sync trigger failed (%s): %s", trigger, exc)
            if trigger == "manual":
                raise
        finally:
            self._lock.release()


scheduler = HourlySyncScheduler()
