import app  # noqa: F401
from flask import Flask

from app.config import settings
from app.database import init_db
from app.routes.dashboard import bp as dashboard_bp


def create_app() -> Flask:
    app_instance = Flask(__name__, template_folder="../templates")
    app_instance.config["SECRET_KEY"] = settings.app_secret_key
    init_db()
    app_instance.register_blueprint(dashboard_bp)
    return app_instance
