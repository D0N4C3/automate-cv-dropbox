import logging

import app  # noqa: F401
from flask import Flask

from app.config import settings
from app.database import init_db
from app.routes.dashboard import bp as dashboard_bp
from app.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    setup_logging(settings.log_level)
    app_instance = Flask(__name__, template_folder="../templates")
    app_instance.config["SECRET_KEY"] = settings.app_secret_key
    init_db()
    app_instance.register_blueprint(dashboard_bp)

    @app_instance.before_request
    def _log_request() -> None:
        from flask import request

        logger.info("HTTP request method=%s path=%s remote=%s", request.method, request.path, request.remote_addr)

    @app_instance.errorhandler(Exception)
    def _handle_unexpected_error(exc: Exception):
        logger.exception("Unhandled Flask exception: %s", exc)
        return "Internal Server Error", 500

    logger.info("Flask app initialized for dashboard")
    return app_instance
