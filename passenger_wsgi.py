"""WSGI entrypoint for Namecheap/cPanel Python App deployments."""

import app  # noqa: F401
from app.web import create_app

application = create_app()
app = application
