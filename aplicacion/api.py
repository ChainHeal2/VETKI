"""API endpoints para lector QR, vacunación y analítica epidemiológica."""
from datetime import date
import re

from flask import Blueprint, jsonify, render_template, request, session
import click
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError
from flask.cli import with_appcontext
from werkzeug.datastructures import MultiDict

from aplicacion.auth.auth import login_required
from aplicacion.db import get_db
from aplicacion.forms.vaccination.vaccination_form import VaccinationForm
from aplicacion.services.vaccine_service import (
    fetch_pet_vaccinations,
    register_vaccination,
    fetch_upcoming_vaccination_alerts,
)
from aplicacion.services.health_service import fetch_disease_analytics

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

_QR_SAFE = re.compile(r"^[A-Za-z0-9._:/+\- ]{1,100}$")


# --- Funciones auxiliares de seguridad ---

def _csrf_error():
    if not current_testing_csrf_enabled():
        return None
    token = request.headers.get("X-CSRFToken") or request.headers.get("X-CSRF-Token")
    if not token:
        return jsonify(error="Token CSRF requerido"), 400
    try:
        validate_csrf(token)
    except ValidationError:
        return jsonify(error="Token CSRF inválido"), 400
    return None


def current_testing_csrf_enabled():
    from flask import current_app
    return current_app.config.get("WTF_CSRF_ENABLED", True)


def _owned_pet(cursor, pet_id):
    cursor.execute(
        "SELECT pet_id, pet_names, pet_microchip FROM vetki.pet_data "
        "WHERE pet_id = %s AND pet_user_id = %s",
        (pet_id, session["user_id"]),
    )
    return cursor.fetchone()


def _clean_qr(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not _QR_SAFE.fullmatch(value):
        return None
    return value


# --- Endpoints del Lector QR ---

@bp.post("/qr/process")
@limiter.limit("10 per minute")
@login_required
def process_qr():
    """Valida un QR y evita consultar mascotas fuera del usuario autenticado."""
    csrf_error = _csrf_error()
    if csrf_error:
        return csrf_error
    payload = request.get_json(silent=True) or {}
    content = _clean_qr(payload.get("content"))
    if content is None:
        return jsonify(error="Contenido QR inválido"), 400

    db, cursor = get_db()
    requested_pet_id = payload.get("pet_id")
    
    if requested_pet_id is not None:
        try:
            pet_id = int(requested_pet_id)
        except (TypeError, ValueError):
            return jsonify(error="pet_id inválido"), 400
        pet = _owned_pet(cursor, pet_id)
        if pet is None:
            return jsonify(error="No autorizado"), 403
        if content != str(pet["pet_microchip"] or ""):
            return jsonify(error="El QR no corresponde a la mascota"), 400
        return jsonify(pet_id=pet_id, microchip=content, pet_name=pet["pet_names"]), 200

    return jsonify(pet_id=None, microchip=content, pet_name=None), 200


# --- Endpoints de Vacunación ---

@bp.get("/vaccinations/<int:pet_id>")
@login_required
def list_vaccinations(pet_id):
    db, cursor = get_db()
    if _owned_pet(cursor, pet_id) is None:
        return jsonify(error="No autorizado"), 403

    vaccinations = fetch_pet_vaccinations(pet_id)
    return jsonify(vaccinations=vaccinations), 200


@bp.post("/vaccinations/<int:pet_id>")
@login_required
def create_vaccination(pet_id):
    csrf_error = _csrf_error()
    if csrf_error:
        return csrf_error

    db, cursor = get_db()
    if _owned_pet(cursor, pet_id) is None:
        return jsonify(error="No autorizado"), 403

    payload = request.get_json(silent=True) or {}

    # Filtrar valores None/vacíos para evitar convertir None a string en MultiDict
    clean_data = {k: v for k, v in payload.items() if v is not None and v != ""}

    # Instancia del formulario WTForms mediante MultiDict
    form = VaccinationForm(formdata=MultiDict(clean_data))

    if not form.validate():
        # Captura el primer mensaje de error que arroje WTForms / VaccinationForm
        first_error = next(iter(form.errors.values()))[0]
        return jsonify(error=first_error), 400

    try:
        vaccination_id = register_vaccination(
            pet_id=pet_id,
            vaccine_name=form.vaccine_name.data,
            application_date=form.application_date.data,
            next_due_date=form.next_due_date.data,
            lot_number=form.lot_number.data,
            notes=form.veterinarian_notes.data,
        )

        return jsonify(
            id=vaccination_id, 
            next_due_date=form.next_due_date.data.isoformat() if form.next_due_date.data else None
        ), 201

    except Exception as e:
        if "vaccination_due_after_application" in str(e):
            return jsonify(error="La fecha de próxima dosis no puede ser anterior a la de aplicación."), 400
        return jsonify(error="Error interno al registrar la vacuna."), 500


# --- Endpoints de Analítica Epidemiológica ---

@bp.get("/analytics/diseases")
@login_required
def disease_analytics():
    """Retorna datos epidemiológicos procesados por el servicio."""
    diseases, source = fetch_disease_analytics(region="cl", period_days=30)
    return jsonify(
        source=source, 
        period_days=30, 
        diseases=diseases
    ), 200


@bp.get("/analytics")
@login_required
def analytics_dashboard():
    """Renderiza la vista principal del dashboard de enfermedades."""
    return render_template("analytics/diseases.html")


# --- Comandos CLI ---

@click.command("check-vaccination-alerts")
@with_appcontext
def check_vaccination_alerts_command():
    """Comando CLI para consultar alertas."""
    alerts = fetch_upcoming_vaccination_alerts(days_ahead=7)
    for alert in alerts:
        click.echo(
            f"{alert['pet_names']}: {alert['vaccine_name']} "
            f"({alert['next_due_date'].isoformat()})"
        )