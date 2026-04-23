from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User

JOB_POSITIONS = ["CEO", "COO", "HR Manager", "Deputy Manager"]


def get_user_count(db: Session) -> int:
    return db.execute(select(func.count()).select_from(User)).scalar_one()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def create_user(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    job_position: str,
) -> tuple[bool, str]:
    normalized_email = email.strip().lower()
    if job_position not in JOB_POSITIONS:
        return False, "Invalid job position selected."
    if get_user_by_email(db, normalized_email):
        return False, "Email is already in use."

    user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=normalized_email,
        password_hash=generate_password_hash(password),
        job_position=job_position,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return False, "Unable to create user right now. Please try again."
    return True, "User created successfully."


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email.strip().lower())
    if not user:
        return None
    if not check_password_hash(user.password_hash, password):
        return None
    return user
