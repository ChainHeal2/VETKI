"""Utilidades compartidas por los controladores API."""

from flask import current_app, jsonify, request, session
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError


def get_db():
    """Resuelve la conexión desde el módulo principal para facilitar su sustitución."""
    from aplicacion.api import get_db as api_get_db

    return api_get_db()


def csrf_error():
    """Valida el token CSRF de solicitudes JSON cuando la protección está activa."""
    if not current_app.config.get("WTF_CSRF_ENABLED", True):
        return None

    token = request.headers.get("X-CSRFToken") or request.headers.get("X-CSRF-Token")
    if not token:
        return jsonify(error="Token CSRF requerido"), 400
    try:
        validate_csrf(token)
    except ValidationError:
        return jsonify(error="Token CSRF inválido"), 400
    return None


def owned_pet(cursor, pet_id):
    """Busca una mascota que pertenezca al usuario autenticado."""
    cursor.execute(
        "SELECT pet_id, pet_names, pet_microchip FROM vetki.pet_data "
        "WHERE pet_id = %s AND pet_user_id = %s",
        (pet_id, session["user_id"]),
    )
    return cursor.fetchone()
