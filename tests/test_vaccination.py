from unittest.mock import MagicMock, patch


def test_vaccination_rejects_invalid_date(authenticated):
    cursor = MagicMock()
    cursor.fetchone.return_value = {"pet_id": 1, "pet_names": "Luna"}
    with patch("aplicacion.api.get_db", return_value=(MagicMock(), cursor)):
        response = authenticated.post(
            "/api/vaccinations/1",
            json={"vaccine_name": "Rabia", "application_date": "31-12-2026"},
        )
    assert response.status_code == 400


def test_vaccination_requires_existing_pet(authenticated):
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    with patch("aplicacion.api.get_db", return_value=(MagicMock(), cursor)):
        response = authenticated.post(
            "/api/vaccinations/404",
            json={"vaccine_name": "Rabia", "application_date": "2026-09-04"},
        )
    assert response.status_code == 403
