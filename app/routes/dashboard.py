import logging
import math
from functools import wraps

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from app.database import SessionLocal
from app.models import User
from app.services.applicant_service import (
    STATUS_OPTIONS,
    get_dashboard_summary,
    list_applicants,
    list_distinct_roles,
    update_applicant_status,
)
from app.services.scheduler_service import scheduler
from app.services.user_service import JOB_POSITIONS, authenticate_user, create_user, get_user_count

bp = Blueprint("dashboard", __name__)
logger = logging.getLogger(__name__)

CONFIDENCE_OPTIONS = ["High", "Medium", "Low"]


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.current_user is None:
            return redirect(url_for("dashboard.login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user() -> None:
    user_id = session.get("user_id")
    if not user_id:
        g.current_user = None
        return

    with SessionLocal() as db:
        g.current_user = db.get(User, user_id)


@bp.get("/login")
def login():
    if g.current_user is not None:
        return redirect(url_for("dashboard.index"))

    with SessionLocal() as db:
        can_register = get_user_count(db) == 0

    return render_template("login.html", can_register=can_register, job_positions=JOB_POSITIONS)


@bp.post("/login")
def login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    with SessionLocal() as db:
        user = authenticate_user(db, email=email, password=password)

    if user is None:
        flash("Invalid email or password.", "danger")
        return redirect(url_for("dashboard.login"))

    session.clear()
    session["user_id"] = user.id
    flash("Logged in successfully.", "success")
    return redirect(url_for("dashboard.index"))


@bp.post("/register")
def register_first_user():
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    job_position = request.form.get("job_position", "").strip()

    if not all([first_name, last_name, email, password, job_position]):
        flash("All fields are required.", "danger")
        return redirect(url_for("dashboard.login"))

    with SessionLocal() as db:
        if get_user_count(db) > 0:
            flash("Registration from login page is disabled.", "danger")
            return redirect(url_for("dashboard.login"))

        ok, message = create_user(
            db,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            job_position=job_position,
        )

    flash(message, "success" if ok else "danger")
    return redirect(url_for("dashboard.login"))


@bp.get("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("dashboard.login"))


@bp.get("/")
@login_required
def index():
    query = request.args.get("q", "").strip() or None
    role = request.args.get("role", "").strip() or None
    status = request.args.get("status", "").strip() or None
    confidence = request.args.get("confidence", "").strip() or None
    date_from = request.args.get("date_from", "").strip() or None
    date_to = request.args.get("date_to", "").strip() or None
    page = max(int(request.args.get("page", "1") or "1"), 1)
    page_size = 10

    with SessionLocal() as db:
        applicants, total = list_applicants(
            db,
            query=query,
            role=role,
            date_from=date_from,
            date_to=date_to,
            status=status,
            confidence=confidence,
            page=page,
            page_size=page_size,
        )
        summary = get_dashboard_summary(db)
        roles = list_distinct_roles(db)

    total_pages = max(math.ceil(total / page_size), 1)

    return render_template(
        "index.html",
        applicants=applicants,
        summary=summary,
        roles=roles,
        confidence_options=CONFIDENCE_OPTIONS,
        status_options=STATUS_OPTIONS,
        page=page,
        total_pages=total_pages,
        total=total,
        filters={
            "q": query or "",
            "role": role or "",
            "status": status or "",
            "confidence": confidence or "",
            "date_from": date_from or "",
            "date_to": date_to or "",
        },
    )


@bp.get("/users/new")
@login_required
def new_user_form():
    return render_template("new_user.html", job_positions=JOB_POSITIONS)


@bp.post("/users")
@login_required
def create_user_post():
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    job_position = request.form.get("job_position", "").strip()

    if not all([first_name, last_name, email, password, job_position]):
        flash("All fields are required.", "danger")
        return redirect(url_for("dashboard.new_user_form"))

    with SessionLocal() as db:
        ok, message = create_user(
            db,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            job_position=job_position,
        )

    flash(message, "success" if ok else "danger")
    return redirect(url_for("dashboard.new_user_form" if not ok else "dashboard.index"))


@bp.post("/sync-now")
@login_required
def sync_now():
    logger.info("Manual sync requested from dashboard remote=%s", request.remote_addr)
    try:
        scheduler.run_now()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Manual sync failed: %s", exc)
        flash("Sync failed. Check logs for details.", "danger")
    else:
        flash("Sync completed. Refresh to see newly processed applicants.", "success")
    return redirect(url_for("dashboard.index"))


@bp.post("/applicants/<int:applicant_id>/status")
@login_required
def set_status(applicant_id: int):
    selected_status = request.form.get("status", "").strip()
    redirect_url = request.form.get("redirect_to") or url_for("dashboard.index")
    with SessionLocal() as db:
        ok = update_applicant_status(db, applicant_id, selected_status)

    if ok:
        flash("Applicant status updated successfully.", "success")
    else:
        flash("Unable to update applicant status.", "danger")
    return redirect(redirect_url)
