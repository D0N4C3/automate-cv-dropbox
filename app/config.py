import os
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Settings:
    imap_server: str = os.getenv("IMAP_SERVER", "")
    imap_port: int = int(os.getenv("IMAP_PORT", "993"))
    email_user: str = os.getenv("EMAIL_USER", "")
    email_pass: str = os.getenv("EMAIL_PASS", "")
    dropbox_app_key: str = os.getenv("DROPBOX_APP_KEY", "")
    dropbox_app_secret: str = os.getenv("DROPBOX_APP_SECRET", "")
    dropbox_refresh_token: str = os.getenv("DROPBOX_REFRESH_TOKEN", "")
    dropbox_access_token: str = os.getenv("DROPBOX_ACCESS_TOKEN", "")
    dropbox_base_path: str = os.getenv("DROPBOX_BASE_PATH", "/CVs")
    database_url: str = os.getenv("DATABASE_URL", "mysql+pymysql://user:pass@localhost/db_name")
    app_secret_key: str = os.getenv("APP_SECRET_KEY", "dev-secret")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    timezone: str = os.getenv("TIMEZONE", "UTC")
    enable_hourly_sync: bool = os.getenv("ENABLE_HOURLY_SYNC", "true").lower() in {"1", "true", "yes"}
    sync_interval_minutes: int = int(os.getenv("SYNC_INTERVAL_MINUTES", "60"))
    initial_backfill_date: date = date(2026, 1, 1)


settings = Settings()
