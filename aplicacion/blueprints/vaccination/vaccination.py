"""CRUD de vacunaciones asociado a las mascotas del usuario."""

from flask import Blueprint, current_app, jsonify, request, session
from flask_wtf.csrf import validate_csrf
from werkzeug.datastructures import MultiDict
from wtforms.validators import ValidationError

from aplicacion.db import get_db
from aplicacion.forms.vaccination.vaccination_form import VaccinationForm
from aplicacion.blueprints.vaccination.vaccination_model import VaccinationModel

bp = Blueprint("vaccination", __name__, url_prefix="/api/vaccinations")


def _first_form_error(form):
    """Obtiene el primer error de validación para la respuesta JSON."""
    return next(iter(form.errors.values()))[0]


def _vaccination_form(payload):
    """Prepara el JSON para WTForms; el token CSRF llega por la cabecera HTTP."""
    form_data = {
        field: "" if value is None else value
        for field, value in payload.items()
    }
    return VaccinationForm(
        formdata=MultiDict(form_data),
        meta={"csrf": False},
    )


def _request_payload():
    """Devuelve el objeto JSON recibido o una respuesta 400 si no es válido."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, (jsonify(error="El cuerpo JSON debe ser un objeto."), 400)
    return payload, None


def _csrf_error():
    """Valida el token enviado por la interfaz en el header de la petición."""
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


def _database_error():
    """Devuelve un mensaje seguro si falla una operación de base de datos."""
    return jsonify(error="Error interno al guardar la vacuna."), 500


def _pet_access_error(pet_id):
    """Comprueba que la mascota pertenezca al usuario autenticado."""
    _, cursor = get_db()
    cursor.execute(
        "SELECT pet_id FROM vetki.pet_data "
        "WHERE pet_id = %s AND pet_user_id = %s",
        (pet_id, session["user_id"]),
    )
    if cursor.fetchone() is None:
        return jsonify(error="No autorizado"), 403
    return None


def _vaccination_data(form):
    """Prepara los campos validados con los nombres usados en la tabla."""
    return {
        "vaccine_name": form.vaccine_name.data,
        "lot_number": form.lot_number.data,
        "veterinarian_notes": form.veterinarian_notes.data,
    }


@bp.get("/<int:pet_id>")
def vaccination_read(pet_id):
    """Lista las vacunas de una mascota que pertenece al usuario."""
    error = _pet_access_error(pet_id)
    if error:
        return error
    vaccinations = VaccinationModel.get_by_pet(pet_id)
    return jsonify(vaccinations=[item.to_dict() for item in vaccinations]), 200


@bp.post("/<int:pet_id>")
def vaccination_create(pet_id):
    """Valida y registra una vacuna para la mascota indicada."""
    error = _csrf_error()
    if error:
        return error

    error = _pet_access_error(pet_id)
    if error:
        return error

    payload, error = _request_payload()
    if error:
        return error
    form = _vaccination_form(payload)
    if not form.validate():
        return jsonify(error=_first_form_error(form)), 400

    try:
        vaccination_id = VaccinationModel.create(pet_id, _vaccination_data(form))
    except Exception:
        return _database_error()
    return jsonify(id=vaccination_id), 201


@bp.get("/<int:pet_id>/<int:vaccination_id>")
def vaccination_read_one(pet_id, vaccination_id):
    """Devuelve los datos de una vacuna específica."""
    error = _pet_access_error(pet_id)
    if error:
        return error

    vaccination = VaccinationModel.get_by_id(pet_id, vaccination_id)
    if vaccination is None:
        return jsonify(error="Vacuna no encontrada."), 404
    return jsonify(vaccination=vaccination.to_dict()), 200


@bp.route("/<int:pet_id>/<int:vaccination_id>", methods=["PUT", "PATCH"])
def vaccination_update(pet_id, vaccination_id):
    """Actualiza todos o algunos campos de una vacuna."""
    error = _csrf_error()
    if error:
        return error

    error = _pet_access_error(pet_id)
    if error:
        return error

    current_vaccination = VaccinationModel.get_by_id(pet_id, vaccination_id)
    if current_vaccination is None:
        return jsonify(error="Vacuna no encontrada."), 404

    payload, error = _request_payload()
    if error:
        return error
    if request.method == "PATCH":
        payload = {**current_vaccination.to_dict(), **payload}

    form = _vaccination_form(payload)
    if not form.validate():
        return jsonify(error=_first_form_error(form)), 400

    try:
        updated = current_vaccination.update(_vaccination_data(form))
    except Exception:
        return _database_error()

    if not updated:
        return jsonify(error="Vacuna no encontrada."), 404
    return jsonify(vaccination_id=vaccination_id, message="Vacuna actualizada."), 200


@bp.delete("/<int:pet_id>/<int:vaccination_id>")
def vaccination_delete(pet_id, vaccination_id):
    """Elimina una vacuna de la mascota indicada."""
    error = _csrf_error()
    if error:
        return error

    error = _pet_access_error(pet_id)
    if error:
        return error

    vaccination = VaccinationModel.get_by_id(pet_id, vaccination_id)
    if vaccination is None:
        return jsonify(error="Vacuna no encontrada."), 404
    if not vaccination.delete():
        return jsonify(error="Vacuna no encontrada."), 404
    return "", 204
