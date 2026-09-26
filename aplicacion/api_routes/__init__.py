"""Registro de las rutas agrupadas por funcionalidad de la API."""

from .analytics import register_analytics_routes
from .qr import register_qr_routes


def register_routes(blueprint, limiter):
    """Conecta los controladores de API al blueprint principal."""
    register_qr_routes(blueprint, limiter)
    register_analytics_routes(blueprint)
