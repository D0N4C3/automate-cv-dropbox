import logging
import os

import app  # noqa: F401
from flask import Flask, Response
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import settings
from app.database import init_db
from app.routes.dashboard import bp as dashboard_bp
from app.services.scheduler_service import scheduler
from app.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


class URLPrefixMiddleware:
    """Ensure Flask routing and url_for() respect an app URL prefix."""

    def __init__(self, app, prefix: str):
        self.app = app
        self.prefix = prefix.rstrip("/") if prefix != "/" else ""

    def __call__(self, environ, start_response):
        if not self.prefix:
            return self.app(environ, start_response)

        path_info = environ.get("PATH_INFO", "")
        script_name = environ.get("SCRIPT_NAME", "")

        if path_info.startswith(self.prefix):
            environ["PATH_INFO"] = path_info[len(self.prefix) :] or "/"
            environ["SCRIPT_NAME"] = f"{script_name}{self.prefix}"

        return self.app(environ, start_response)


def _resolve_url_prefix() -> str:
    raw_prefix = (os.getenv("APP_URL_PREFIX") or os.getenv("PASSENGER_BASE_URI") or "").strip()
    if not raw_prefix:
        return ""
    if not raw_prefix.startswith("/"):
        raw_prefix = f"/{raw_prefix}"
    return raw_prefix.rstrip("/") or "/"


def create_app() -> Flask:
    setup_logging(settings.log_level)
    app_instance = Flask(__name__, template_folder="../templates")
    app_instance.config["SECRET_KEY"] = settings.app_secret_key
    app_instance.wsgi_app = ProxyFix(app_instance.wsgi_app, x_proto=1, x_host=1, x_prefix=1)

    url_prefix = _resolve_url_prefix()
    if url_prefix:
        app_instance.wsgi_app = URLPrefixMiddleware(app_instance.wsgi_app, prefix=url_prefix)
        app_instance.config["APPLICATION_ROOT"] = url_prefix

    init_db()
    app_instance.register_blueprint(dashboard_bp)

    if settings.enable_hourly_sync:
        scheduler.start()

    @app_instance.before_request
    def _log_request() -> None:
        from flask import request

        logger.info("HTTP request method=%s path=%s remote=%s", request.method, request.path, request.remote_addr)

    @app_instance.route("/favicon.ico")
    def favicon() -> Response:
        return Response(status=204)

    @app_instance.errorhandler(HTTPException)
    def _handle_http_error(exc: HTTPException):
        logger.info("HTTP exception status=%s description=%s", exc.code, exc.description)
        return exc

    @app_instance.errorhandler(Exception)
    def _handle_unexpected_error(exc: Exception):
        logger.exception("Unhandled Flask exception: %s", exc)
        return "Internal Server Error", 500

    logger.info("Flask app initialized for dashboard")
    return app_instance
