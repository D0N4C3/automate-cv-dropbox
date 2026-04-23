import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.database import SessionLocal
from app.services.applicant_service import search_applicants
from app.services.sync_service import SyncService

bp = Blueprint("dashboard", __name__)
logger = logging.getLogger(__name__)


@bp.get("/")
def index():
    query = request.args.get("q", "").strip() or None
    role = request.args.get("role", "").strip() or None
    date_from = request.args.get("date_from", "").strip() or None
    date_to = request.args.get("date_to", "").strip() or None

    with SessionLocal() as db:
        applicants = search_applicants(db, query=query, role=role, date_from=date_from, date_to=date_to)

    return render_template(
        "index.html",
        applicants=applicants,
        filters={"q": query or "", "role": role or "", "date_from": date_from or "", "date_to": date_to or ""},
    )


@bp.post("/sync-now")
def sync_now():
    logger.info("Manual sync requested from dashboard remote=%s", request.remote_addr)
    try:
        SyncService().run()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Manual sync failed: %s", exc)
        flash("Sync failed. Check logs for details.", "danger")
    else:
        flash("Sync completed. Refresh to see newly processed applicants.", "success")
    return redirect(url_for("dashboard.index"))
