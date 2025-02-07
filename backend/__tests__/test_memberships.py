import pytest
from starlette.testclient import TestClient
from backend import app

@pytest.fixture
def client():
    """Test client for HTTP request tests."""
    with TestClient(app) as test_client:
        yield test_client

def test_get_chat_accounts(client):
    response = client.get("/chats/1/accounts")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "accounts" in data

def test_get_nonexistent_chat_accounts(client):
    response = client.get("/chats/100/accounts")
    assert response.status_code == 404
    assert response.json() == {"error": "entity_not_found", "message": "Unable to find chat with id=100"}

def test_add_membership(client):
    request_data = {"account_id": 1}
    response = client.post("/chats/1/accounts", json=request_data)
    assert response.status_code == 201
    assert response.json() == {"chat_id": 1, "account_id": 1}

def test_add_existing_membership(client):
    request_data = {"account_id": 1}
    client.post("/chats/1/accounts", json=request_data)
    response = client.post("/chats/1/accounts", json=request_data)
    assert response.status_code == 200
    assert response.json() == {"chat_id": 1, "account_id": 1}

def test_add_membership_invalid_chat(client):
    request_data = {"account_id": 1}
    response = client.post("/chats/999/accounts", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }

def test_add_membership_invalid_account(client):
    request_data = {"account_id": 999}
    response = client.post("/chats/1/accounts", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find account with id=999"
    }

def test_remove_membership(client):
    request_data = {"account_id": 2}
    client.post("/chats/1/accounts", json=request_data)
    response = client.delete("/chats/1/accounts/2")
    assert response.status_code == 204

def test_remove_nonexistent_membership(client):
    response = client.delete("/chats/1/accounts/999")
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=999 must be a member of chat with id=1"
    }

def test_remove_nonexistent_chat(client):
    response = client.delete("/chats/999/accounts/1")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }

def test_remove_chat_owner(client):
    response = client.delete("/chats/1/accounts/1")
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_owner_removal",
        "message": "Unable to remove the owner of a chat"
    }