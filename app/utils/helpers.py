import re
from datetime import datetime
from email.utils import parsedate_to_datetime


NAME_CLEAN = re.compile(r"[^A-Za-z\s'-]")


def normalize_name(name: str) -> str:
    cleaned = NAME_CLEAN.sub(" ", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return " ".join(p.capitalize() for p in cleaned.split())


def parse_email_date(raw_date: str) -> datetime:
    if not raw_date:
        return datetime.utcnow()
    try:
        return parsedate_to_datetime(raw_date).replace(tzinfo=None)
    except Exception:  # noqa: BLE001
        return datetime.utcnow()
