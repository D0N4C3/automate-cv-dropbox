import logging
import math

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.database import SessionLocal
from app.services.applicant_service import (
    STATUS_OPTIONS,
    get_dashboard_summary,
    list_applicants,
    list_distinct_roles,
    update_applicant_status,
)
from app.services.scheduler_service import scheduler

bp = Blueprint("dashboard", __name__)
logger = logging.getLogger(__name__)

CONFIDENCE_OPTIONS = ["High", "Medium", "Low"]


@bp.get("/")
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


@bp.post("/sync-now")
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
