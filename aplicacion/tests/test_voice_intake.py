"""Pruebas del endpoint que devuelve únicamente la transcripción."""

import io
from unittest.mock import Mock

import pytest


ENDPOINT = "/api/clinical-voice-intake"


def _login(client, user_id=1):
    with client.session_transaction() as session:
        session["user_id"] = user_id


@pytest.fixture
def fake_db(monkeypatch):
    cursor = Mock()
    monkeypatch.setattr("aplicacion.blueprints.auth.auth.get_db", lambda: (None, cursor))
    monkeypatch.setattr("aplicacion.blueprints.voice_intake.routes.get_db", lambda: (None, cursor))
    return cursor


def test_requires_login(client):
    response = client.post(ENDPOINT)
    assert response.status_code == 401
    assert "No autorizado" in response.get_json()["error"]


def test_requires_audio(client, fake_db):
    _login(client)
    response = client.post(ENDPOINT, data={"pet_id": "1"})
    assert response.status_code == 400
    assert "audio" in response.get_json()["error"]


def test_rejects_unsupported_audio(client, fake_db):
    _login(client)
    response = client.post(
        ENDPOINT,
        data={"pet_id": "1", "audio": (io.BytesIO(b"audio"), "dictado.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "formato" in response.get_json()["error"].lower()


def test_returns_transcription_without_persisting(client, fake_db, monkeypatch):
    _login(client)
    monkeypatch.setattr(
        "aplicacion.blueprints.voice_intake.routes._verify_pet_ownership",
        lambda cursor, pet_id, user_id: None,
    )
    monkeypatch.setattr(
        "aplicacion.blueprints.voice_intake.routes.transcribe_audio",
        lambda audio_file: "El paciente pesa doce kilos.",
    )

    response = client.post(
        ENDPOINT,
        data={"pet_id": "1", "audio": (io.BytesIO(b"audio"), "dictado.webm")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.get_json() == {"transcription": "El paciente pesa doce kilos."}
