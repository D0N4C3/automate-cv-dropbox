from collections import Counter
from datetime import datetime, time

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models import Applicant, SyncState


STATUS_OPTIONS = ["New", "In Review", "Interview", "Shortlisted", "Offer", "Rejected", "Hired"]


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


def search_applicants(
    db: Session,
    query: str | None,
    role: str | None,
    date_from: str | None,
    date_to: str | None,
    status: str | None = None,
    confidence: str | None = None,
):
    stmt = select(Applicant)
    if query:
        like = f"%{query}%"
        stmt = stmt.where(or_(Applicant.full_name.ilike(like), Applicant.email.ilike(like)))
    if role:
        stmt = stmt.where(Applicant.role == role)
    if status:
        stmt = stmt.where(Applicant.status == status)
    if confidence:
        stmt = stmt.where(Applicant.name_confidence == confidence)
    if date_from:
        parsed_from = _safe_iso_date(date_from)
        if parsed_from:
            stmt = stmt.where(Applicant.date_applied >= datetime.combine(parsed_from.date(), time.min))
    if date_to:
        parsed_to = _safe_iso_date(date_to)
        if parsed_to:
            stmt = stmt.where(Applicant.date_applied <= datetime.combine(parsed_to.date(), time.max))
    return stmt.order_by(Applicant.date_applied.desc())


def list_applicants(
    db: Session,
    query: str | None,
    role: str | None,
    date_from: str | None,
    date_to: str | None,
    status: str | None,
    confidence: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Applicant], int]:
    stmt = search_applicants(db, query, role, date_from, date_to, status=status, confidence=confidence)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    offset = max(page - 1, 0) * page_size
    rows = db.execute(stmt.offset(offset).limit(page_size)).scalars().all()
    return rows, total


def get_dashboard_summary(db: Session) -> dict:
    total = db.execute(select(func.count()).select_from(Applicant)).scalar_one()
    new_count = db.execute(select(func.count()).where(Applicant.status == "New")).scalar_one()
    interview_count = db.execute(select(func.count()).where(Applicant.status == "Interview")).scalar_one()
    hired_count = db.execute(select(func.count()).where(Applicant.status == "Hired")).scalar_one()
    recent = db.execute(
        select(func.count()).where(Applicant.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    ).scalar_one()

    roles = db.execute(select(Applicant.role)).scalars().all()
    statuses = db.execute(select(Applicant.status)).scalars().all()

    return {
        "total": total,
        "new": new_count,
        "interview": interview_count,
        "hired": hired_count,
        "today": recent,
        "role_breakdown": dict(Counter(roles)),
        "status_breakdown": dict(Counter(statuses)),
    }


def update_applicant_status(db: Session, applicant_id: int, status: str) -> bool:
    if status not in STATUS_OPTIONS:
        return False

    applicant = db.get(Applicant, applicant_id)
    if not applicant:
        return False

    applicant.status = status
    db.commit()
    return True


def list_distinct_roles(db: Session) -> list[str]:
    rows = db.execute(select(Applicant.role).distinct().order_by(Applicant.role.asc())).scalars().all()
    return rows
