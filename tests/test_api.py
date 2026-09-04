from unittest.mock import MagicMock, patch


def test_qr_rejects_malformed_payload(authenticated):
    response = authenticated.post("/api/qr/process", json={"content": "<script>"})
    assert response.status_code == 400


def test_qr_rejects_pet_owned_by_another_user(authenticated):
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    with patch("aplicacion.api.get_db", return_value=(MagicMock(), cursor)):
        response = authenticated.post(
            "/api/qr/process", json={"content": "123456", "pet_id": 99}
        )
    assert response.status_code == 403


def test_disease_analytics_returns_json(authenticated):
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    with patch("aplicacion.api.get_db", return_value=(MagicMock(), cursor)):
        response = authenticated.get("/api/analytics/diseases")
    assert response.status_code == 200
    assert len(response.json["diseases"]) == 4
