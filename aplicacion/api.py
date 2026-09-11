"""API segura para lector QR, vacunación y analítica."""
from datetime import date, datetime, time, timedelta
import re

import psycopg2.errors
from flask import Blueprint, jsonify, render_template, request, session
import click
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError
from flask.cli import with_appcontext

from aplicacion.auth.auth import login_required
from aplicacion.db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")
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

_QR_SAFE = re.compile(r"^[A-Za-z0-9._:/+\- ]{1,100}$")
_DISEASES = ("Distemper", "Parvovirus", "PIF", "Leucemia Felina")


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

    # Retorno estructurado garantizado para alta de paciente (Evita congelar el JS)
    return jsonify(pet_id=None, microchip=content, pet_name=None), 200


@bp.get("/vaccinations/<int:pet_id>")
@login_required
def list_vaccinations(pet_id):
    db, cursor = get_db()
    if _owned_pet(cursor, pet_id) is None:
        return jsonify(error="No autorizado"), 403
    cursor.execute(
        "SELECT id, vaccine_name, application_date, next_due_date, lot_number, "
        "veterinarian_notes FROM vetki.vaccinations WHERE pet_id = %s "
        "ORDER BY application_date DESC",
        (pet_id,),
    )
    return jsonify(
        vaccinations=[
            {
                **row,
                "application_date": row["application_date"].isoformat(),
                "next_due_date": row["next_due_date"].isoformat()
                if row["next_due_date"]
                else None,
            }
            for row in cursor.fetchall()
        ]
    ), 200


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
    vaccine_name = str(payload.get("vaccine_name", "")).strip()
    if not 2 <= len(vaccine_name) <= 120:
        return jsonify(error="Nombre de vacuna inválido"), 400
    try:
        application_date = date.fromisoformat(str(payload["application_date"]))
        next_due_date = (
            date.fromisoformat(str(payload["next_due_date"]))
            if payload.get("next_due_date")
            else None
        )
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Formato de fecha inválido"), 400
    if next_due_date and next_due_date < application_date:
        return jsonify(error="La próxima dosis no puede ser anterior"), 400

    cursor.execute(
        "INSERT INTO vetki.vaccinations "
        "(pet_id, vaccine_name, application_date, next_due_date, lot_number, veterinarian_notes) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (
            pet_id,
            vaccine_name,
            application_date,
            next_due_date,
            str(payload.get("lot_number", "")).strip() or None,
            str(payload.get("veterinarian_notes", "")).strip() or None,
        ),
    )
    vaccination_id = cursor.fetchone()["id"]
    if next_due_date:
        cursor.execute(
            "SELECT 1 FROM vetki.appointments WHERE pet_id = %s "
            "AND appointment_date::date = %s LIMIT 1",
            (pet_id, next_due_date),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO vetki.appointments "
                "(appointment_google_event_id, pet_id, appointment_date) "
                "VALUES (%s, %s, %s)",
                (
                    "vaccination-draft",
                    pet_id,
                    datetime.combine(next_due_date, time(9, 0)),
                ),
            )
    db.commit()
    return jsonify(id=vaccination_id, next_due_date=next_due_date.isoformat()
                   if next_due_date else None), 201


@bp.get("/analytics/diseases")
@login_required
def disease_analytics():
    db, cursor = get_db()
    today = date.today()
    current_start = today - timedelta(days=30)
    previous_start = current_start - timedelta(days=30)
    try:
        cursor.execute(
            "SELECT disease_name, "
            "SUM(CASE WHEN report_date >= %s THEN case_count ELSE 0 END) AS current_cases, "
            "SUM(CASE WHEN report_date >= %s AND report_date < %s THEN case_count ELSE 0 END) AS previous_cases "
            "FROM vetki.disease_cases WHERE disease_name = ANY(%s) GROUP BY disease_name",
            (current_start, previous_start, current_start, list(_DISEASES)),
        )
        rows = {row["disease_name"]: row for row in cursor.fetchall()}
    except psycopg2.errors.UndefinedTable:
        db.rollback()
        rows = {}
    result = []
    for disease in _DISEASES:
        row = rows.get(disease, {"current_cases": 0, "previous_cases": 0})
        current = int(row["current_cases"] or 0)
        previous = int(row["previous_cases"] or 0)
        variation = ((current - previous) / previous * 100) if previous else (
            100.0 if current else 0.0
        )
        result.append(
            {"disease": disease, "current_cases": current,
             "previous_cases": previous, "variation_percent": round(variation, 2)}
        )
    return jsonify(period_days=30, diseases=result), 200


@bp.get("/analytics")
@login_required
def analytics_dashboard():
    return render_template("analytics/diseases.html")


def schedule_vaccination_alerts():
    """Devuelve vacunas que deben alertarse exactamente en siete días."""
    db, cursor = get_db()
    target = date.today() + timedelta(days=7)
    cursor.execute(
        "SELECT v.id, v.pet_id, p.pet_names, v.vaccine_name, v.next_due_date "
        "FROM vetki.vaccinations v JOIN vetki.pet_data p ON p.pet_id = v.pet_id "
        "WHERE v.next_due_date = %s ORDER BY v.id",
        (target,),
    )
    return cursor.fetchall()


@click.command("check-vaccination-alerts")
@with_appcontext
def check_vaccination_alerts_command():
    """Lista las vacunas cuyo refuerzo debe alertarse en siete días."""
    alerts = schedule_vaccination_alerts()
    for alert in alerts:
        click.echo(
            f"{alert['pet_names']}: {alert['vaccine_name']} "
            f"({alert['next_due_date'].isoformat()})"
        )