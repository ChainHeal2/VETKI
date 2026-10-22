"""API de dictado por voz: recibe audio y devuelve su transcripción."""

import logging

from flask import Blueprint, jsonify, request, session
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError

from aplicacion.blueprints.auth.auth import login_required
from aplicacion.db import get_db
from aplicacion.services.speech_to_text import (
    ALLOWED_AUDIO_EXTENSIONS,
    MAX_AUDIO_SIZE_BYTES,
    TranscriptionError,
    transcribe_audio,
)

logger = logging.getLogger(__name__)

bp = Blueprint("voice_intake", __name__, url_prefix="/api")


def _csrf_error():
    """Valida el token CSRF enviado en el header de la petición."""
    from flask import current_app

    if not current_app.config.get("WTF_CSRF_ENABLED", True):
        return None

    token = request.headers.get("X-CSRFToken") or request.headers.get("X-CSRF-Token")
    if not token:
        return jsonify(error="Token CSRF requerido."), 400
    try:
        validate_csrf(token)
    except ValidationError:
        return jsonify(error="Token CSRF inválido."), 400
    return None


def _validate_audio_file(audio_file):
    """Comprueba la extensión y el tamaño del audio recibido."""
    filename = audio_file.filename or ""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        return (
            jsonify(
                error=f"Formato de audio no soportado: '.{extension}'. "
                f"Formatos válidos: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
            ),
            400,
        )

    audio_file.stream.seek(0, 2)
    size = audio_file.stream.tell()
    audio_file.stream.seek(0)
    if size > MAX_AUDIO_SIZE_BYTES:
        max_mb = MAX_AUDIO_SIZE_BYTES / (1024 * 1024)
        return jsonify(error=f"El archivo de audio excede el límite de {max_mb:.0f} MB."), 400
    if size == 0:
        return jsonify(error="El archivo de audio está vacío."), 400
    return None


def _get_pet_id():
    """Obtiene y valida el identificador de mascota del formulario."""
    raw_pet_id = request.form.get("pet_id")
    if raw_pet_id is None:
        return None, (jsonify(error="El campo 'pet_id' es obligatorio."), 400)
    try:
        pet_id = int(raw_pet_id)
    except (TypeError, ValueError):
        return None, (jsonify(error="'pet_id' debe ser un número entero válido."), 400)
    if pet_id <= 0:
        return None, (jsonify(error="'pet_id' debe ser un número positivo."), 400)
    return pet_id, None


def _verify_pet_ownership(cursor, pet_id, user_id):
    """Evita transcribir audio asociado a una mascota de otra persona."""
    cursor.execute(
        "SELECT pet_id FROM vetki.pet_data WHERE pet_id = %s AND pet_user_id = %s",
        (pet_id, user_id),
    )
    if cursor.fetchone() is None:
        return jsonify(error="Mascota no encontrada o no autorizada."), 403
    return None


@bp.post("/clinical-voice-intake")
@login_required
def clinical_voice_intake():
    """Transcribe el audio y devuelve texto; no guarda datos clínicos."""
    csrf_err = _csrf_error()
    if csrf_err:
        return csrf_err

    pet_id, pet_err = _get_pet_id()
    if pet_err:
        return pet_err

    audio_file = request.files.get("audio")
    if audio_file is None:
        return jsonify(error="Debe enviar un archivo de audio ('audio')."), 400

    audio_err = _validate_audio_file(audio_file)
    if audio_err is not None:
        return audio_err

    # La sesión ya fue verificada por @login_required.
    _, cursor = get_db()
    ownership_err = _verify_pet_ownership(cursor, pet_id, session["user_id"])
    if ownership_err:
        return ownership_err

    try:
        transcription = transcribe_audio(audio_file)
    except TranscriptionError as exc:
        logger.error("Error al transcribir el dictado: %s", exc)
        return jsonify(error=f"Error al transcribir el audio: {exc}"), 502

    return jsonify(transcription=transcription), 200
