import pytest
from starlette.testclient import TestClient
from backend import app

@pytest.fixture
def client():
    """Test client for HTTP request tests."""
    with TestClient(app) as test_client:
        yield test_client

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