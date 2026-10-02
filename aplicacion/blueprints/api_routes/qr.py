"""Rutas del lector QR."""

import re

from flask import Blueprint
from flask import jsonify, request
from .common import csrf_error, get_db, owned_pet
from aplicacion.limiter import limiter

_QR_SAFE = re.compile(r"^[A-Za-z0-9._:/+\- ]{1,100}$")
bp = Blueprint("qr", __name__, url_prefix="/qr")

def clean_qr(value):
    """Acepta únicamente contenido QR acotado y con caracteres seguros."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value if _QR_SAFE.fullmatch(value) else None

@bp.post("/process")
@limiter.limit("10 per minute")
def process_qr():
    """Valida el QR y restringe las mascotas al usuario autenticado."""
    error = csrf_error()
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    content = clean_qr(payload.get("content"))
    if content is None:
        return jsonify(error="Contenido QR inválido"), 400

    _, cursor = get_db()
    requested_pet_id = payload.get("pet_id")
    if requested_pet_id is not None:
        try:
            pet_id = int(requested_pet_id)
        except (TypeError, ValueError):
            return jsonify(error="pet_id inválido"), 400

        pet = owned_pet(cursor, pet_id)
        if pet is None:
            return jsonify(error="No autorizado"), 403
        if content != str(pet["pet_microchip"] or ""):
            return jsonify(error="El QR no corresponde a la mascota"), 400
        return jsonify(pet_id=pet_id, microchip=content, pet_name=pet["pet_names"]), 200
    return jsonify(pet_id=None, microchip=content, pet_name=None),200