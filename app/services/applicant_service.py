from datetime import datetime, time

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import Applicant, SyncState


def _safe_iso_date(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def get_state(db: Session, key: str) -> str | None:
    row = db.execute(select(SyncState).where(SyncState.key == key)).scalar_one_or_none()
    return row.value if row else None


def set_state(db: Session, key: str, value: str) -> None:
    row = db.execute(select(SyncState).where(SyncState.key == key)).scalar_one_or_none()
    if row:
        row.value = value
    else:
        db.add(SyncState(key=key, value=value))


def applicant_exists(db: Session, message_id: str, cv_file_name: str) -> bool:
    stmt = select(Applicant.id).where(and_(Applicant.message_id == message_id, Applicant.cv_file_name == cv_file_name))
    return db.execute(stmt).first() is not None


def search_applicants(db: Session, query: str | None, role: str | None, date_from: str | None, date_to: str | None) -> list[Applicant]:
    stmt = select(Applicant)
    if query:
        like = f"%{query}%"
        stmt = stmt.where(or_(Applicant.full_name.ilike(like), Applicant.email.ilike(like)))
    if role:
        stmt = stmt.where(Applicant.role == role)
    if date_from:
        parsed_from = _safe_iso_date(date_from)
        if parsed_from:
            stmt = stmt.where(Applicant.date_applied >= datetime.combine(parsed_from.date(), time.min))
    if date_to:
        parsed_to = _safe_iso_date(date_to)
        if parsed_to:
            stmt = stmt.where(Applicant.date_applied <= datetime.combine(parsed_to.date(), time.max))
    stmt = stmt.order_by(Applicant.date_applied.desc())
    return list(db.execute(stmt).scalars())
