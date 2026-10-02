"""API endpoints para lector QR, vacunación y analítica."""
from datetime import date, datetime, time, timedelta
import re

from flask import Blueprint, jsonify, render_template, request, session
import click
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError
from flask.cli import with_appcontext

from aplicacion.blueprints.auth.auth import login_required
from aplicacion.db import get_db
from aplicacion.services.health_service import fetch_disease_analytics  # 👈 Importamos el servicio

bp = Blueprint("analytic", __name__, url_prefix="/api")

# ... (mantener funciones auxiliares como _csrf_error, _owned_pet, _clean_qr, etc.) ...

@bp.get("/analytic/diseases")
def disease_analytics():
    """Endpoint simplificado: delega la lógica al servicio."""
    diseases, source = fetch_disease_analytics(region="cl", period_days=30)
    return jsonify(
        source=source, 
        period_days=30, 
        diseases=diseases
    ), 200


@bp.get("/analytic")
@login_required
def analytics_dashboard():
    return render_template("analytics/diseases.html")