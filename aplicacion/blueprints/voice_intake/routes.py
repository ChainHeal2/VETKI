"""API de Dictado Clínico por Voz — Endpoint de ingreso transaccional multi-tabla.

Blueprint: voice_intake
Ruta principal: POST /api/clinical-voice-intake

Recibe un archivo de audio o una transcripción de texto, invoca el servicio de IA
para extraer datos clínicos estructurados y los persiste de forma transaccional en:
  - vetki.pet_data (actualización de peso y temperatura)
  - vetki.medical_records (nuevo registro clínico)
  - vetki.vaccinations (prescripciones / fármacos recetados)
"""

import logging
from datetime import date

from flask import Blueprint, jsonify, request, session
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError

from aplicacion.db import get_db
from aplicacion.services.voice_ai import (
    ALLOWED_AUDIO_EXTENSIONS,
    MAX_AUDIO_SIZE_BYTES,
    VoiceAIError,
    process_voice_input,
)

logger = logging.getLogger(__name__)

bp = Blueprint("voice_intake", __name__, url_prefix="/api")


# ---------------------------------------------------------------------------
# Helpers de validación de request
# ---------------------------------------------------------------------------
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
    """Valida extensión y tamaño del archivo de audio.

    Returns:
        Tupla (None, None) si es válido, o (jsonify_response, status_code) si hay error.
    """
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

    # Verificar tamaño leyendo la longitud del stream
    audio_file.stream.seek(0, 2)  # ir al final
    size = audio_file.stream.tell()
    audio_file.stream.seek(0)  # volver al inicio
    if size > MAX_AUDIO_SIZE_BYTES:
        max_mb = MAX_AUDIO_SIZE_BYTES / (1024 * 1024)
        return (
            jsonify(error=f"El archivo de audio excede el límite de {max_mb:.0f} MB."),
            400,
        )
    if size == 0:
        return jsonify(error="El archivo de audio está vacío."), 400

    return None, None


def _get_pet_id_from_request():
    """Extrae y valida el pet_id del payload (JSON o form-data).

    Returns:
        (pet_id: int, error_response) — uno de los dos será None.
    """
    # Puede venir como form field o como JSON
    raw_pet_id = request.form.get("pet_id") or (
        request.get_json(silent=True) or {}
    ).get("pet_id")

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
    """Verifica que la mascota pertenezca al usuario autenticado.

    Returns:
        None si es válido, o (jsonify_response, status_code) si no autorizado.
    """
    cursor.execute(
        "SELECT pet_id FROM vetki.pet_data WHERE pet_id = %s AND pet_user_id = %s",
        (pet_id, user_id),
    )
    if cursor.fetchone() is None:
        return jsonify(error="Mascota no encontrada o no autorizada."), 403
    return None


# ---------------------------------------------------------------------------
# Funciones de persistencia transaccional
# ---------------------------------------------------------------------------
def _update_patient(cursor, pet_id, patient_updates):
    """Actualiza peso y temperatura en pet_data si se proporcionan valores.

    Nota: pet_data no tiene columnas weight_kg / temperature_c directamente,
    pero medical_records sí. Sin embargo, el plan original solicita actualizar
    pet_data. Como las columnas no existen, guardamos estos valores como parte
    del registro médico (se manejan en _insert_medical_record).
    """
    # Las constantes vitales se guardan en medical_records, no en pet_data.
    # Esta función queda como placeholder por si en el futuro se agregan columnas.
    pass


def _insert_medical_record(cursor, pet_id, user_id, clinical_record, patient_updates):
    """Inserta un nuevo registro en medical_records con los datos extraídos.

    Args:
        cursor: cursor de psycopg2.
        pet_id: ID de la mascota.
        user_id: ID del veterinario autenticado.
        clinical_record: dict con 'diagnosis' y 'observations'.
        patient_updates: dict con 'weight_kg' y 'temperature_c'.

    Returns:
        int: ID del registro médico creado.
    """
    sql = """
        INSERT INTO vetki.medical_records (
            medical_record_reason,
            medical_record_weight,
            medical_record_temperature,
            medical_record_date,
            medical_record_diagnosis,
            medical_record_treatment,
            medical_record_medical_history,
            medical_record_pet_id,
            medical_record_user_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING medical_record_id
    """
    params = (
        "dictado",  # reason: indica que proviene de dictado por voz
        patient_updates.get("weight_kg"),
        patient_updates.get("temperature_c"),
        date.today(),
        clinical_record.get("diagnosis"),
        None,  # treatment: se registra en vaccinations como prescripciones
        clinical_record.get("observations"),
        pet_id,
        user_id,
    )
    cursor.execute(sql, params)
    row = cursor.fetchone()
    return row["medical_record_id"]


def _insert_prescriptions(cursor, pet_id, prescriptions):
    """Inserta las prescripciones como registros en vaccinations.

    Cada prescripción se guarda con el nombre del fármaco como 'vaccine_name'
    y los detalles (dosis, frecuencia, duración) en 'veterinarian_notes'.

    Args:
        cursor: cursor de psycopg2.
        pet_id: ID de la mascota.
        prescriptions: lista de dicts con drug_name, dosage, frequency, duration.

    Returns:
        list[int]: IDs de las prescripciones insertadas.
    """
    if not prescriptions:
        return []

    inserted_ids = []
    sql = """
        INSERT INTO vetki.vaccinations (
            pet_id,
            vaccine_name,
            application_date,
            veterinarian_notes
        ) VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    for rx in prescriptions:
        notes = (
            f"Dosis: {rx['dosage']} | "
            f"Frecuencia: {rx['frequency']} | "
            f"Duración: {rx['duration']}"
        )
        cursor.execute(sql, (pet_id, rx["drug_name"], date.today(), notes))
        row = cursor.fetchone()
        inserted_ids.append(row["id"])

    return inserted_ids


# ---------------------------------------------------------------------------
# Endpoint principal
# ---------------------------------------------------------------------------
@bp.post("/clinical-voice-intake")
def clinical_voice_intake():
    """Procesa un dictado clínico (audio o texto) y lo persiste transaccionalmente.

    Acepta:
      - multipart/form-data con campo 'audio' (archivo) y 'pet_id'.
      - multipart/form-data con campo 'transcription' (texto) y 'pet_id'.
      - application/json con campos 'transcription' y 'pet_id'.

    Responde:
      - 201: datos guardados correctamente.
      - 400: error de validación.
      - 401: no autenticado.
      - 403: mascota no pertenece al usuario.
      - 500: error interno.
    """
    # --- 1. Validar CSRF ---
    csrf_err = _csrf_error()
    if csrf_err:
        return csrf_err

    # --- 2. Verificar sesión (sin usar decorador login_required) ---
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify(error="No autorizado. Inicie sesión para acceder a este recurso."), 401

    # --- 3. Obtener y validar pet_id ---
    pet_id, pet_err = _get_pet_id_from_request()
    if pet_err:
        return pet_err

    # --- 4. Verificar propiedad de la mascota ---
    db, cursor = get_db()
    ownership_err = _verify_pet_ownership(cursor, pet_id, user_id)
    if ownership_err:
        return ownership_err

    # --- 5. Obtener entrada (audio o texto) ---
    audio_file = request.files.get("audio")
    transcription_text = (
        request.form.get("transcription")
        or (request.get_json(silent=True) or {}).get("transcription")
    )

    if audio_file is None and not transcription_text:
        return (
            jsonify(
                error="Debe enviar un archivo de audio ('audio') o un texto de transcripción ('transcription')."
            ),
            400,
        )

    # Validar audio si se proporcionó
    if audio_file is not None:
        audio_err, audio_status = _validate_audio_file(audio_file)
        if audio_err is not None:
            return audio_err, audio_status

    # --- 6. Procesar con IA ---
    try:
        clinical_data = process_voice_input(
            audio_file=audio_file,
            transcription_text=transcription_text,
        )
    except VoiceAIError as exc:
        logger.error("Error en servicio de IA: %s", exc)
        return jsonify(error=f"Error al procesar el dictado: {exc}"), 502
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    # --- 7. Persistir transaccionalmente ---
    patient_updates = clinical_data.get("patient_updates", {})
    clinical_record = clinical_data.get("clinical_record", {})
    prescriptions = clinical_data.get("prescriptions", [])

    try:
        # Actualizar constantes vitales (placeholder)
        _update_patient(cursor, pet_id, patient_updates)

        # Insertar registro clínico
        medical_record_id = _insert_medical_record(
            cursor, pet_id, user_id, clinical_record, patient_updates
        )

        # Insertar prescripciones
        prescription_ids = _insert_prescriptions(cursor, pet_id, prescriptions)

        # Commit atómico: todo o nada
        db.commit()
        logger.info(
            "Dictado clínico guardado: medical_record_id=%s, prescriptions=%s (pet_id=%s, user_id=%s)",
            medical_record_id,
            prescription_ids,
            pet_id,
            user_id,
        )
    except Exception as exc:
        db.rollback()
        logger.error(
            "Error transaccional al guardar dictado clínico (pet_id=%s): %s",
            pet_id,
            exc,
        )
        return (
            jsonify(error="Error interno al guardar los datos clínicos. Se revirtieron todos los cambios."),
            500,
        )

    # --- 8. Respuesta exitosa ---
    return (
        jsonify(
            message="Datos clínicos guardados correctamente.",
            medical_record_id=medical_record_id,
            prescription_ids=prescription_ids,
            patient_updates=patient_updates,
            clinical_record=clinical_record,
            prescriptions=prescriptions,
            summary={
                "weight_kg": patient_updates.get("weight_kg"),
                "temperature_c": patient_updates.get("temperature_c"),
                "diagnosis": clinical_record.get("diagnosis"),
                "observations": clinical_record.get("observations"),
                "prescriptions_count": len(prescriptions),
            },
        ),
        201,
    )


