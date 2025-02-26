import pytest
from starlette.testclient import TestClient
from backend import app
from backend.database.auth_service import AuthService


@pytest.fixture
def client():
    """Test client for HTTP request tests."""
    with TestClient(app) as test_client:
        yield test_client
USER_ID = 1
USERNAME = "testuser"
EMAIL = "test@example.com"
PASSWORD = "password"
TOKEN = AuthService.create_access_token(USER_ID)
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def test_get_accounts(client):
    response = client.get("/accounts")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "accounts" in data

def test_get_nonexistent_account(client):
    response = client.get("/accounts/100")
    assert response.status_code == 404
    assert response.json() == {"error": "entity_not_found", "message": "Unable to find account with id=100"}


def test_get_current_account(client):
    response = client.get("/accounts/me", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["username"] == USERNAME


def test_update_current_account(client):
    response = client.put("/accounts/me", headers=HEADERS, json={"username": "updateduser", "email": "updated@example.com"})
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"
    assert response.json()["email"] == "updated@example.com"


def test_update_current_account_duplicate_username(client):
    response = client.put("/accounts/me", headers=HEADERS, json={"username": "existinguser"})
    assert response.status_code == 422
    assert response.json()["error"] == "duplicate_entity_value"


def test_update_current_account_duplicate_email(client):
    response = client.put("/accounts/me", headers=HEADERS, json={"email": "existing@example.com"})
    assert response.status_code == 422
    assert response.json()["error"] == "duplicate_entity_value"


def test_update_password(client):
    response = client.put("/accounts/me/password", headers=HEADERS, data={"old_password": PASSWORD, "new_password": "newpassword"})
    assert response.status_code == 204


def test_update_password_invalid_old_password(client):
    response = client.put("/accounts/me/password", headers=HEADERS, data={"old_password": "wrongpassword", "new_password": "newpassword"})
    assert response.status_code == 401
    assert response.json()["error"] == "invalid_credentials"


def test_delete_current_account(client):
    response = client.delete("/accounts/me", headers=HEADERS)
    assert response.status_code == 204


def test_delete_current_account_owner_of_chats(client):
    response = client.delete("/accounts/me", headers=HEADERS)
    assert response.status_code == 422
    assert response.json()["error"] == "chat_owner_removal"


# ✅ Error handling tests

def test_access_token_required(client):
    response = client.get("/accounts/me")
    assert response.status_code == 403
    assert response.json()["error"] == "authentication_required"


def test_invalid_access_token(client, monkeypatch):
    def mock_decode(token):
        raise ValueError("invalid_access_token")
    monkeypatch.setattr(AuthService, "decode_access_token", mock_decode)

    response = client.get("/accounts/me", headers=HEADERS)
    assert response.status_code == 403
    assert response.json()["error"] == "invalid_access_token"


# ✅ Summary
# - Added tests for GET /accounts/me, PUT /accounts/me, PUT /accounts/me/password, and DELETE /accounts/me
# - Included error cases for duplicate username, duplicate email, invalid password, and token errors
# - Uses HEADERS with Bearer token for authenticated routes
