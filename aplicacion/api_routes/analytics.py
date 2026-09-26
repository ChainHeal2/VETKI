"""Rutas de analítica epidemiológica."""

from flask import jsonify, render_template

from aplicacion.auth.auth import login_required
from aplicacion.services.health_service import fetch_disease_analytics


def register_analytics_routes(blueprint):
    @blueprint.get("/analytics/diseases")
    @login_required
    def disease_analytics():
        """Entrega el resumen epidemiológico preparado por el servicio."""
        diseases, source = fetch_disease_analytics(region="cl", period_days=30)
        return jsonify(source=source, period_days=30, diseases=diseases), 200

    @blueprint.get("/analytics")
    @login_required
    def analytics_dashboard():
        """Renderiza el dashboard de enfermedades."""
        return render_template("analytics/diseases.html")
