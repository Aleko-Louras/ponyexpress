import pytest
from starlette.testclient import TestClient
from backend import app

@pytest.fixture
def client():
    """Test client for HTTP request tests."""
    with TestClient(app) as test_client:
        yield test_client

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

def test_create_message(client):
    request_data = {"text": "Hello!", "account_id": 1}
    response = client.post("/chats/1/messages", json=request_data)
    assert response.status_code == 201
    assert response.json()["text"] == "Hello!"

def test_create_message_invalid_chat(client):
    request_data = {"text": "Hello!", "account_id": 1}
    response = client.post("/chats/999/messages", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }

def test_create_message_invalid_account(client):
    request_data = {"text": "Hello!", "account_id": 999}
    response = client.post("/chats/1/messages", json=request_data)
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=999 must be a member of chat with id=1"
    }

def test_update_message(client):
    request_data = {"text": "Updated message"}
    response = client.put("/chats/1/messages/1", json=request_data)
    assert response.status_code == 200
    assert response.json()["text"] == "Updated message"

def test_update_message_nonexistent_chat(client):
    request_data = {"text": "Updated message"}
    response = client.put("/chats/999/messages/1", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }

def test_update_message_nonexistent_message(client):
    request_data = {"text": "Updated message"}
    response = client.put("/chats/1/messages/999", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find message with id=999"
    }

def test_delete_message(client):
    response = client.delete("/chats/1/messages/1")
    assert response.status_code == 204

def test_delete_nonexistent_chat_message(client):
    response = client.delete("/chats/999/messages/1")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=999"
    }

def test_delete_nonexistent_message(client):
    response = client.delete("/chats/1/messages/999")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find message with id=999"
    }