import pytest
from starlette.testclient import TestClient
from backend import app

@pytest.fixture
def client():
    """Test client for HTTP request tests."""
    with TestClient(app) as test_client:
        yield test_client

def test_get_chats(client):
    response = client.get("/chats")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "chats" in data

def test_get_nonexistent_chat(client):
    response = client.get("/chats/100")
    assert response.status_code == 404
    assert response.json() == {"error": "entity_not_found", "message": "Unable to find chat with id=100"}

def test_get_chat_messages(client):
    response = client.get("/chats/1/messages")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "messages" in data

def test_get_nonexistent_chat_messages(client):
    response = client.get("/chats/100/messages")
    assert response.status_code == 404
    assert response.json() == {"error": "entity_not_found", "message": "Unable to find chat with id=100"}

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

def test_create_chat(client):
    response = client.post("/chats", json={"name": "New Chat", "owner_id": 1})
    assert response.status_code == 201
    assert response.json()["name"] == "New Chat"

def test_create_chat_duplicate_name(client):
    client.post("/chats", json={"name": "Duplicate Chat", "owner_id": 1})
    response = client.post("/chats", json={"name": "Duplicate Chat", "owner_id": 1})
    assert response.status_code == 422
    assert response.json()["error"] == "duplicate_entity_value"

def test_create_chat_invalid_owner(client):
    response = client.post("/chats", json={"name": "Invalid Owner Chat", "owner_id": 999})
    assert response.status_code == 404
    assert response.json()["error"] == "entity_not_found"

def test_update_chat(client):
    response = client.put("/chats/1", json={"name": "Updated Chat"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Chat"

def test_update_chat_invalid_owner(client):
    response = client.put("/chats/1", json={"owner_id": 999})
    assert response.status_code == 404
    assert response.json()["error"] == "entity_not_found"

def test_update_chat_non_member_owner(client):
    response = client.put("/chats/1", json={"owner_id": 3})
    assert response.status_code == 422
    assert response.json()["error"] == "chat_membership_required"

def test_delete_chat(client):
    response = client.delete("/chats/1")
    assert response.status_code == 204

def test_delete_nonexistent_chat(client):
    response = client.delete("/chats/999")
    assert response.status_code == 404
    assert response.json()["error"] == "entity_not_found"