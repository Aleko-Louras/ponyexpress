#Exception classes for different exception types

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

class ChatOwnerRemoval(Exception):
    def __init__(self):
        self.error = "chat_owner_removal"
        self.message = "Unable to remove the owner of a chat"

class InvalidCredentials(Exception):
    """Exception raised for invalid username or password."""
    def __init__(self):
        self.error = "invalid_credentials"
        self.message = "Authentication failed: invalid username or password"
class AuthenticationRequired(Exception):
    """Exception raised when no access token is provided."""
    def __init__(self):
        self.error = "authentication_required"
        self.message = "Not authenticated"

class ExpiredAccessToken(Exception):
    """Exception raised when the access token has expired."""
    def __init__(self):
        self.error = "expired_access_token"
        self.message = "Authentication failed: expired access token"

class InvalidAccessToken(Exception):
    """Exception raised when the access token is invalid."""
    def __init__(self):
        self.error = "invalid_access_token"
        self.message = "Authentication failed: invalid access token"
class AccessDenied(Exception):
    """Exception raised when a user attempts to perform an unauthorized action."""
    def __init__(self, message: str):
        self.error = "access_denied"
        self.message = message