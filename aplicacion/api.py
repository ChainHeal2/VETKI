"""Registro de rutas auxiliares de la API y limitación de peticiones."""
from flask import Blueprint
from aplicacion.db import get_db

# Instancia global de Flask-Limiter
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address, default_limits=[])
except ImportError:
    class _NoopLimiter:
        def limit(self, _limit):
            return lambda view: view

        def init_app(self, _app):
            return None

    limiter = _NoopLimiter()

bp = Blueprint("api", __name__, url_prefix="/api")

from aplicacion.api_routes import register_routes

register_routes(bp, limiter)
