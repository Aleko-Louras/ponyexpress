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

# ✅ Auth Tests

def test_register_user(client):
    response = client.post("/auth/registration", data={
        "username": USERNAME,
        "email": EMAIL,
        "password": PASSWORD
    })
    assert response.status_code == 201
    assert response.json()["username"] == USERNAME


def test_login_user(client):
    response = client.post("/auth/token", data={
        "username": USERNAME,
        "password": PASSWORD
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_web_login(client):
    response = client.post("/auth/web/login", data={
        "username": USERNAME,
        "password": PASSWORD
    })
    assert response.status_code == 204
    assert "pony_express_token" in response.cookies


def test_web_logout(client):
    response = client.post("/auth/web/logout", headers=HEADERS)
    assert response.status_code == 204

# ✅ Auth Error Tests

def test_access_token_required(client):
    response = client.get("/accounts/me")
    assert response.status_code == 403
    assert response.json()["error"] == "authentication_required"


def test_expired_access_token(client, monkeypatch):
    def mock_decode(token):
        raise ValueError("expired_access_token")
    monkeypatch.setattr(AuthService, "decode_access_token", mock_decode)

    response = client.get("/accounts/me", headers=HEADERS)
    assert response.status_code == 403
    assert response.json()["error"] == "expired_access_token"


def test_invalid_access_token(client, monkeypatch):
    def mock_decode(token):
        raise ValueError("invalid_access_token")
    monkeypatch.setattr(AuthService, "decode_access_token", mock_decode)

    response = client.get("/accounts/me", headers=HEADERS)
    assert response.status_code == 403
    assert response.json()["error"] == "invalid_access_token"


def test_duplicate_username(client):
    response = client.post("/auth/registration", data={
        "username": USERNAME,
        "email": "new@example.com",
        "password": PASSWORD
    })
    assert response.status_code == 422
    assert response.json()["error"] == "duplicate_entity_value"


def test_duplicate_email(client):
    response = client.post("/auth/registration", data={
        "username": "newuser",
        "email": EMAIL,
        "password": PASSWORD
    })
    assert response.status_code == 422
    assert response.json()["error"] == "duplicate_entity_value"

# ✅ Run Tests
if __name__ == "__main__":
    pytest.main()

# ✅ Summary
# - Auth tests include register, login, web login, and logout
# - Error tests cover missing token, expired token, invalid token, and duplicate values
# - Structured using Pytest fixtures for clean and modular testing
