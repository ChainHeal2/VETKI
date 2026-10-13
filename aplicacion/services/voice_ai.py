"""Servicio de integración con IA para dictado clínico veterinario.

Responsabilidades:
  1. Transcribir audio a texto (OpenAI Whisper).
  2. Extraer datos estructurados del texto (GPT con function calling).

Variables de entorno requeridas:
  - OPENAI_API_KEY: clave de la API de OpenAI.
"""

import json
import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"
CHAT_URL = "https://api.openai.com/v1/chat/completions"
REQUEST_TIMEOUT = 30  # segundos

# Extensiones de audio aceptadas
ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "m4a", "webm", "ogg", "flac", "mp4"}
MAX_AUDIO_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

# ---------------------------------------------------------------------------
# Esquema JSON que el modelo de IA debe devolver
# ---------------------------------------------------------------------------
CLINICAL_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "patient_updates": {
            "type": "object",
            "properties": {
                "weight_kg": {"type": ["number", "null"]},
                "temperature_c": {"type": ["number", "null"]},
            },
            "required": ["weight_kg", "temperature_c"],
            "additionalProperties": False,
        },
        "clinical_record": {
            "type": "object",
            "properties": {
                "diagnosis": {"type": ["string", "null"]},
                "observations": {"type": ["string", "null"]},
            },
            "required": ["diagnosis", "observations"],
            "additionalProperties": False,
        },
        "prescriptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string"},
                    "dosage": {"type": "string"},
                    "frequency": {"type": "string"},
                    "duration": {"type": "string"},
                },
                "required": ["drug_name", "dosage", "frequency", "duration"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["patient_updates", "clinical_record", "prescriptions"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Prompt del sistema para la extracción
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
Eres un asistente veterinario clínico que extrae datos estructurados de un dictado médico.
A partir del texto dictado, devuelve ÚNICAMENTE un objeto JSON que cumpla exactamente este esquema:

{
  "patient_updates": {
    "weight_kg": <float o null>,
    "temperature_c": <float o null>
  },
  "clinical_record": {
    "diagnosis": <string o null>,
    "observations": <string o null>
  },
  "prescriptions": [
    {
      "drug_name": <string>,
      "dosage": <string>,
      "frequency": <string>,
      "duration": <string>
    }
  ]
}

Reglas:
- Si un dato no se menciona, usa null (para campos escalares) o lista vacía (para prescriptions).
- No inventes datos que no estén presentes en el dictado.
- Responde SOLO con el JSON, sin texto adicional ni bloques de código.
"""


def _auth_headers() -> dict:
    """Cabeceras de autenticación comunes para la API de OpenAI."""
    return {"Authorization": f"Bearer {OPENAI_API_KEY}"}


# ---------------------------------------------------------------------------
# 1. Transcripción de audio
# ---------------------------------------------------------------------------
def transcribe_audio(audio_file) -> str:
    """Envía un archivo de audio a Whisper y devuelve la transcripción.

    Args:
        audio_file: objeto tipo FileStorage (Werkzeug) con el audio.

    Returns:
        Texto transcrito.

    Raises:
        VoiceAIError: si la llamada falla o la respuesta es inválida.
    """
    try:
        response = requests.post(
            WHISPER_URL,
            headers=_auth_headers(),
            files={"file": (audio_file.filename, audio_file.stream, audio_file.content_type)},
            data={"model": "whisper-1", "language": "es"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()
        text = result.get("text", "").strip()
        if not text:
            raise VoiceAIError("Whisper devolvió una transcripción vacía.")
        logger.info("Audio transcrito exitosamente (%d caracteres).", len(text))
        return text
    except requests.RequestException as exc:
        logger.error("Error al transcribir audio con Whisper: %s", exc)
        raise VoiceAIError(f"Error al transcribir audio: {exc}") from exc


# ---------------------------------------------------------------------------
# 2. Extracción estructurada con GPT
# ---------------------------------------------------------------------------
def extract_clinical_data(transcription_text: str) -> dict:
    """Envía la transcripción a GPT y extrae los datos clínicos estructurados.

    Args:
        transcription_text: texto del dictado (ya transcrito o ingresado directamente).

    Returns:
        Diccionario con la estructura del JSON Schema clínico.

    Raises:
        VoiceAIError: si la llamada falla o el JSON no es parseable.
    """
    payload = {
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcription_text},
        ],
    }
    try:
        response = requests.post(
            CHAT_URL,
            headers={**_auth_headers(), "Content-Type": "application/json"},
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        # Limpiar posibles bloques de código markdown
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            content = content.rsplit("```", 1)[0]
        data = json.loads(content)
        logger.info("Datos clínicos extraídos correctamente por GPT.")
        return data
    except (requests.RequestException, json.JSONDecodeError, KeyError, IndexError) as exc:
        logger.error("Error al extraer datos clínicos con GPT: %s", exc)
        raise VoiceAIError(f"Error al extraer datos clínicos: {exc}") from exc


# ---------------------------------------------------------------------------
# 3. Función principal orquestadora
# ---------------------------------------------------------------------------
def process_voice_input(
    audio_file=None,
    transcription_text: Optional[str] = None,
) -> dict:
    """Orquesta la transcripción (si hay audio) y extracción de datos clínicos.

    Debe recibir al menos uno de los dos parámetros.

    Args:
        audio_file: archivo de audio (FileStorage) — opcional.
        transcription_text: texto ya transcrito — opcional.

    Returns:
        Diccionario validado con la estructura del JSON Schema clínico.

    Raises:
        VoiceAIError: si ocurre un error en cualquier etapa.
        ValueError: si no se proporciona ninguna entrada.
    """
    if audio_file is None and not transcription_text:
        raise ValueError("Debe proporcionar un archivo de audio o una transcripción de texto.")

    # Si hay audio, transcribir primero
    if audio_file is not None:
        transcription_text = transcribe_audio(audio_file)

    # Extraer datos estructurados
    raw_data = extract_clinical_data(transcription_text)

    # Validar y normalizar la estructura
    validated = validate_clinical_data(raw_data)

    return validated


# ---------------------------------------------------------------------------
# 4. Validación del JSON devuelto por la IA
# ---------------------------------------------------------------------------
def validate_clinical_data(data: dict) -> dict:
    """Valida y normaliza el JSON extraído contra el esquema esperado.

    No usamos Marshmallow/Pydantic para no agregar dependencias externas;
    la validación sigue el patrón manual del proyecto.

    Args:
        data: diccionario crudo devuelto por GPT.

    Returns:
        Diccionario normalizado con valores seguros.

    Raises:
        VoiceAIError: si la estructura no es válida.
    """
    if not isinstance(data, dict):
        raise VoiceAIError("La respuesta de la IA no es un objeto JSON válido.")

    # --- patient_updates ---
    patient_updates = data.get("patient_updates")
    if not isinstance(patient_updates, dict):
        patient_updates = {}
    weight_kg = _to_float_or_none(patient_updates.get("weight_kg"))
    temperature_c = _to_float_or_none(patient_updates.get("temperature_c"))

    # Rangos razonables para veterinaria
    if weight_kg is not None and not (0.01 <= weight_kg <= 2000):
        logger.warning("Peso fuera de rango (%s kg), se descarta.", weight_kg)
        weight_kg = None
    if temperature_c is not None and not (30.0 <= temperature_c <= 45.0):
        logger.warning("Temperatura fuera de rango (%s °C), se descarta.", temperature_c)
        temperature_c = None

    # --- clinical_record ---
    clinical_record = data.get("clinical_record")
    if not isinstance(clinical_record, dict):
        clinical_record = {}
    diagnosis = _sanitize_string(clinical_record.get("diagnosis"))
    observations = _sanitize_string(clinical_record.get("observations"))

    # --- prescriptions ---
    raw_prescriptions = data.get("prescriptions")
    if not isinstance(raw_prescriptions, list):
        raw_prescriptions = []

    prescriptions = []
    for item in raw_prescriptions:
        if not isinstance(item, dict):
            continue
        drug_name = _sanitize_string(item.get("drug_name"))
        if not drug_name:
            continue  # prescripción sin nombre de fármaco se descarta
        prescriptions.append({
            "drug_name": drug_name,
            "dosage": _sanitize_string(item.get("dosage")) or "",
            "frequency": _sanitize_string(item.get("frequency")) or "",
            "duration": _sanitize_string(item.get("duration")) or "",
        })

    return {
        "patient_updates": {
            "weight_kg": weight_kg,
            "temperature_c": temperature_c,
        },
        "clinical_record": {
            "diagnosis": diagnosis,
            "observations": observations,
        },
        "prescriptions": prescriptions,
    }


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _to_float_or_none(value) -> Optional[float]:
    """Convierte a float, retornando None si no es posible."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sanitize_string(value) -> Optional[str]:
    """Limpia y sanitiza un string; devuelve None si está vacío."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip()
    return value if value else None


# ---------------------------------------------------------------------------
# Excepciones del módulo
# ---------------------------------------------------------------------------
class VoiceAIError(Exception):
    """Error genérico del servicio de voz/IA."""

