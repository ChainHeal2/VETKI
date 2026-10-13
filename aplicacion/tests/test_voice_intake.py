"""Tests para el endpoint POST /api/clinical-voice-intake.

Valida:
  - Autenticación requerida (sesión activa).
  - Validación de parámetros obligatorios (pet_id, audio o texto).
  - Manejo de errores del servicio de IA.
  - Flujo exitoso con transcripción de texto.
"""

import io
import json
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
ENDPOINT = "/api/clinical-voice-intake"

MOCK_AI_RESPONSE = {
    "patient_updates": {"weight_kg": 12.5, "temperature_c": 38.7},
    "clinical_record": {
        "diagnosis": "Dermatitis alérgica",
        "observations": "Lesiones en zona ventral, prurito intenso.",
    },
    "prescriptions": [
        {
            "drug_name": "Prednisolona",
            "dosage": "0.5 mg/kg",
            "frequency": "Cada 12 horas",
            "duration": "5 días",
        }
    ],
}


def _login(client, user_id=1):
    """Simula una sesión de usuario autenticado."""
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = "Dr. Test"
        sess["user_email"] = "test@vetki.cl"
        sess["user_role"] = "veterinario"


# ---------------------------------------------------------------------------
# Tests de autenticación
# ---------------------------------------------------------------------------
class TestAuthRequired:
    """El endpoint debe rechazar peticiones sin sesión activa."""

    def test_returns_401_without_session(self, client):
        response = client.post(
            ENDPOINT,
            json={"pet_id": 1, "transcription": "El paciente pesa 12 kg"},
        )
        assert response.status_code == 401
        data = response.get_json()
        assert "No autorizado" in data["error"]


# ---------------------------------------------------------------------------
# Tests de validación de entrada
# ---------------------------------------------------------------------------
class TestInputValidation:
    """Valida que el endpoint rechace entradas incompletas o inválidas."""

    def test_missing_pet_id(self, client):
        _login(client)
        response = client.post(
            ENDPOINT,
            json={"transcription": "El paciente pesa 12 kg"},
        )
        assert response.status_code == 400
        assert "pet_id" in response.get_json()["error"]

    def test_invalid_pet_id_string(self, client):
        _login(client)
        response = client.post(
            ENDPOINT,
            json={"pet_id": "abc", "transcription": "Texto"},
        )
        assert response.status_code == 400

    def test_missing_audio_and_transcription(self, client):
        _login(client)
        # Mockear get_db para que before_app_request (auth) y la ruta no necesiten DB real
        mock_cursor = type("C", (), {"execute": lambda s, *a, **kw: None, "fetchone": lambda s: None})()
        mock_conn = type("D", (), {"commit": lambda s: None, "rollback": lambda s: None})()
        with patch("aplicacion.blueprints.auth.auth.get_db", return_value=(mock_conn, mock_cursor)):
            with patch("aplicacion.blueprints.voice_intake.routes.get_db", return_value=(mock_conn, mock_cursor)):
                with patch("aplicacion.blueprints.voice_intake.routes._verify_pet_ownership", return_value=None):
                    response = client.post(
                        ENDPOINT,
                        data={"pet_id": "1"},
                        content_type="multipart/form-data",
                    )
        assert response.status_code == 400
        assert "audio" in response.get_json()["error"].lower() or "transcri" in response.get_json()["error"].lower()

    def test_empty_audio_file(self, client):
        _login(client)
        data = {
            "pet_id": "1",
            "audio": (io.BytesIO(b""), "empty.mp3"),
        }
        mock_cursor = type("C", (), {"execute": lambda s, *a, **kw: None, "fetchone": lambda s: None})()
        mock_conn = type("D", (), {"commit": lambda s: None, "rollback": lambda s: None})()
        with patch("aplicacion.blueprints.auth.auth.get_db", return_value=(mock_conn, mock_cursor)):
            with patch(
                "aplicacion.blueprints.voice_intake.routes._verify_pet_ownership",
                return_value=None,
            ):
                with patch("aplicacion.blueprints.voice_intake.routes.get_db", return_value=(mock_conn, mock_cursor)):
                    response = client.post(
                        ENDPOINT,
                        data=data,
                        content_type="multipart/form-data",
                    )
        assert response.status_code == 400
        assert "vacío" in response.get_json()["error"].lower() or "empty" in response.get_json()["error"].lower()

    def test_unsupported_audio_format(self, client):
        _login(client)
        data = {
            "pet_id": "1",
            "audio": (io.BytesIO(b"\x00" * 100), "recording.txt"),
        }
        mock_cursor = type("C", (), {"execute": lambda s, *a, **kw: None, "fetchone": lambda s: None})()
        mock_conn = type("D", (), {"commit": lambda s: None, "rollback": lambda s: None})()
        with patch("aplicacion.blueprints.auth.auth.get_db", return_value=(mock_conn, mock_cursor)):
            with patch(
                "aplicacion.blueprints.voice_intake.routes._verify_pet_ownership",
                return_value=None,
            ):
                with patch("aplicacion.blueprints.voice_intake.routes.get_db", return_value=(mock_conn, mock_cursor)):
                    response = client.post(
                        ENDPOINT,
                        data=data,
                        content_type="multipart/form-data",
                    )
        assert response.status_code == 400
        assert "formato" in response.get_json()["error"].lower() or "soportado" in response.get_json()["error"].lower()


# ---------------------------------------------------------------------------
# Tests de flujo exitoso
# ---------------------------------------------------------------------------
class TestSuccessFlow:
    """Verifica el flujo completo con mocks del servicio de IA y la BD."""

    @patch("aplicacion.blueprints.voice_intake.routes.process_voice_input")
    @patch("aplicacion.blueprints.voice_intake.routes._verify_pet_ownership")
    @patch("aplicacion.blueprints.voice_intake.routes.get_db")
    def test_text_transcription_success(
        self, mock_get_db, mock_ownership, mock_ai, client
    ):
        _login(client)

        # Mock de la BD
        mock_cursor = type("MockCursor", (), {
            "execute": lambda self, *a, **kw: None,
            "fetchone": lambda self: {"medical_record_id": 42, "id": 99},
        })()
        mock_conn = type("MockConn", (), {
            "commit": lambda self: None,
            "rollback": lambda self: None,
        })()
        mock_get_db.return_value = (mock_conn, mock_cursor)
        mock_ownership.return_value = None
        mock_ai.return_value = MOCK_AI_RESPONSE

        response = client.post(
            ENDPOINT,
            json={"pet_id": 1, "transcription": "El paciente pesa 12.5 kg, temperatura 38.7"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Datos clínicos guardados correctamente."
        assert data["medical_record_id"] is not None
        assert "summary" in data

    @patch("aplicacion.blueprints.voice_intake.routes.process_voice_input")
    @patch("aplicacion.blueprints.voice_intake.routes._verify_pet_ownership")
    @patch("aplicacion.blueprints.voice_intake.routes.get_db")
    def test_db_rollback_on_error(
        self, mock_get_db, mock_ownership, mock_ai, client
    ):
        """Verifica que se haga rollback si falla la inserción."""
        _login(client)

        mock_conn = type("MockConn", (), {
            "commit": lambda self: (_ for _ in ()).throw(Exception("DB error")),
            "rollback": lambda self: None,
        })()
        mock_cursor = type("MockCursor", (), {
            "execute": lambda self, *a, **kw: None,
            "fetchone": lambda self: {"medical_record_id": 42, "id": 99},
        })()
        mock_get_db.return_value = (mock_conn, mock_cursor)
        mock_ownership.return_value = None
        mock_ai.return_value = MOCK_AI_RESPONSE

        response = client.post(
            ENDPOINT,
            json={"pet_id": 1, "transcription": "Peso 10 kg"},
        )
        # Debería responder 500 y hacer rollback
        assert response.status_code == 500
        assert "revirtieron" in response.get_json()["error"].lower()


# ---------------------------------------------------------------------------
# Tests del servicio de IA
# ---------------------------------------------------------------------------
class TestAIServiceErrors:
    """Verifica el manejo de errores del servicio de IA."""

    @patch("aplicacion.blueprints.voice_intake.routes.process_voice_input")
    @patch("aplicacion.blueprints.voice_intake.routes._verify_pet_ownership")
    @patch("aplicacion.blueprints.voice_intake.routes.get_db")
    def test_voice_ai_error_returns_502(
        self, mock_get_db, mock_ownership, mock_ai, client
    ):
        from aplicacion.services.voice_ai import VoiceAIError

        _login(client)
        mock_conn = type("MockConn", (), {"commit": lambda s: None, "rollback": lambda s: None})()
        mock_cursor = type("MockCursor", (), {"execute": lambda s, *a, **kw: None, "fetchone": lambda s: None})()
        mock_get_db.return_value = (mock_conn, mock_cursor)
        mock_ownership.return_value = None
        mock_ai.side_effect = VoiceAIError("Timeout en Whisper")

        response = client.post(
            ENDPOINT,
            json={"pet_id": 1, "transcription": "Texto de prueba"},
        )
        assert response.status_code == 502
        assert "error" in response.get_json()


# ---------------------------------------------------------------------------
# Tests de validación del JSON de IA (voice_ai.validate_clinical_data)
# ---------------------------------------------------------------------------
class TestValidateClinicalData:
    """Verifica la función de validación/normalización del JSON de la IA."""

    def test_valid_data(self):
        from aplicacion.services.voice_ai import validate_clinical_data

        result = validate_clinical_data(MOCK_AI_RESPONSE)
        assert result["patient_updates"]["weight_kg"] == 12.5
        assert result["clinical_record"]["diagnosis"] == "Dermatitis alérgica"
        assert len(result["prescriptions"]) == 1

    def test_missing_sections_returns_defaults(self):
        from aplicacion.services.voice_ai import validate_clinical_data

        result = validate_clinical_data({})
        assert result["patient_updates"]["weight_kg"] is None
        assert result["patient_updates"]["temperature_c"] is None
        assert result["clinical_record"]["diagnosis"] is None
        assert result["prescriptions"] == []

    def test_out_of_range_weight_discarded(self):
        from aplicacion.services.voice_ai import validate_clinical_data

        data = {
            "patient_updates": {"weight_kg": 99999, "temperature_c": 38.0},
            "clinical_record": {"diagnosis": None, "observations": None},
            "prescriptions": [],
        }
        result = validate_clinical_data(data)
        assert result["patient_updates"]["weight_kg"] is None  # descartado
        assert result["patient_updates"]["temperature_c"] == 38.0

    def test_out_of_range_temperature_discarded(self):
        from aplicacion.services.voice_ai import validate_clinical_data

        data = {
            "patient_updates": {"weight_kg": 10.0, "temperature_c": 100.0},
            "clinical_record": {"diagnosis": None, "observations": None},
            "prescriptions": [],
        }
        result = validate_clinical_data(data)
        assert result["patient_updates"]["temperature_c"] is None  # descartado

    def test_prescription_without_drug_name_discarded(self):
        from aplicacion.services.voice_ai import validate_clinical_data

        data = {
            "patient_updates": {"weight_kg": None, "temperature_c": None},
            "clinical_record": {"diagnosis": None, "observations": None},
            "prescriptions": [
                {"drug_name": "", "dosage": "1mg", "frequency": "diario", "duration": "5 días"},
                {"drug_name": "Amoxicilina", "dosage": "500mg", "frequency": "c/8h", "duration": "7 días"},
            ],
        }
        result = validate_clinical_data(data)
        assert len(result["prescriptions"]) == 1
        assert result["prescriptions"][0]["drug_name"] == "Amoxicilina"

    def test_non_dict_raises_error(self):
        from aplicacion.services.voice_ai import validate_clinical_data, VoiceAIError

        with pytest.raises(VoiceAIError):
            validate_clinical_data("not a dict")
