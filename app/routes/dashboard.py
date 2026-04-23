from flask import Blueprint, render_template, request

from app.database import SessionLocal
from app.services.applicant_service import search_applicants

bp = Blueprint("dashboard", __name__)


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
