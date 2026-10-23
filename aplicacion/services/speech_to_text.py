"""Transcripción local de audio con Vosk; no llama a servicios externos."""

import json
import logging
import os
import subprocess
from pathlib import Path
from threading import Lock

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "m4a", "webm", "ogg", "flac", "mp4"}
MAX_AUDIO_SIZE_BYTES = 5 * 1024 * 1024
SAMPLE_RATE = 16000
MODEL_PATH = Path(
    os.environ.get(
        "VOSK_MODEL_PATH",
        Path(__file__).resolve().parents[2] / "models" / "vosk-model-small-es-0.42",
    )
)
_model = None
_model_lock = Lock()


class TranscriptionError(Exception):
    """Error al convertir el audio o ejecutar el motor local de voz."""


def _get_model():
    """Carga Vosk una vez por proceso para reutilizar el modelo entre solicitudes."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                if not MODEL_PATH.is_dir():
                    raise TranscriptionError(
                        f"No se encontró el modelo de voz en {MODEL_PATH}. "
                        "Descarga el modelo español indicado en las instrucciones del proyecto."
                    )
                try:
                    from vosk import Model
                except ImportError as exc:
                    raise TranscriptionError(
                        "Falta instalar Vosk en el entorno virtual (pip install -r requirements.txt)."
                    ) from exc
                _model = Model(str(MODEL_PATH))
    return _model


def transcribe_audio(audio_file) -> str:
    """Transcribe el archivo recibido localmente y devuelve texto plano.

    FFmpeg decodifica los formatos que MediaRecorder puede generar a PCM mono
    de 16 kHz. Vosk procesa ese PCM sin enviar audio a una API externa.
    """
    audio_file.stream.seek(0)
    audio_bytes = audio_file.stream.read()
    if not audio_bytes:
        raise TranscriptionError("El archivo de audio está vacío.")

    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
        "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "s16le", "pipe:1",
    ]
    try:
        decoded = subprocess.run(
            command,
            input=audio_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=60,
        )
    except subprocess.TimeoutExpired as exc:
        raise TranscriptionError("Se agotó el tiempo al convertir el audio.") from exc

    if decoded.returncode != 0 or not decoded.stdout:
        detail = decoded.stderr.decode("utf-8", errors="replace").strip()
        logger.warning("FFmpeg no pudo decodificar el audio: %s", detail)
        raise TranscriptionError("No se pudo leer el formato de audio recibido.")
    try:
        from vosk import KaldiRecognizer
    except ImportError as exc:
        raise TranscriptionError(
            "Falta instalar Vosk en el entorno virtual (pip install -r requirements.txt)."
        ) from exc

    recognizer = KaldiRecognizer(_get_model(), SAMPLE_RATE)
    recognizer.SetWords(False)
    recognizer.AcceptWaveform(decoded.stdout)
    result = json.loads(recognizer.FinalResult())
    text = result.get("text", "").strip()
    if not text:
        raise TranscriptionError("No se detectó voz en la grabación.")

    logger.info("Audio transcrito localmente (%d caracteres).", len(text))
    return text
