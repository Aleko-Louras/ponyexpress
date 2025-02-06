from fastapi import HTTPException

class EntityNotFound(Exception):
    def __init__(self, entity_name: str, entity_id: int):
        self.error = "entity_not_found"
        self.message = f"Unable to find {entity_name} with id={entity_id}"

class DuplicateEntityValue(Exception):
    def __init__(self, entity_name: str, field_name: str, field_value: str):
        self.error = "duplicate_entity_value"
        self.message = f"Duplicate value: {entity_name} with {field_name}={field_value} already exists"


class ChatMembershipRequired(Exception):
    def __init__(self, account_id: int, chat_id: int):
        self.error = "chat_membership_required"
        self.message = f"Account with id={account_id} must be a member of chat with id={chat_id}"


class ChatOwnerRemoval(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail={
                "error": "chat_owner_removal",
                "message": "Unable to remove the owner of a chat"
            },
        )