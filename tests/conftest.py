import pytest
from unittest.mock import MagicMock, patch

from aplicacion import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SECRET_KEY="test-key")
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def isolated_auth_db():
    cursor = MagicMock()
    cursor.fetchone.return_value = {
        "user_id": 1, "user_role": "veterinario", "user_names": "Test"
    }
    with patch("aplicacion.auth.auth.get_db", return_value=(MagicMock(), cursor)):
        yield


@pytest.fixture()
def authenticated(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["user_role"] = "veterinario"
    return client
