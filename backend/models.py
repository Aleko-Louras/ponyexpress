from pydantic import BaseModel
from datetime import datetime

class Metadata(BaseModel):
    count: int

class Account(BaseModel):
    id: int
    username: str
class AccountWithEmail(Account):
    email: str
class Chat(BaseModel):
    id: int
    name: str
    owner_id: int

class Message(BaseModel):
    id: int
    text: str
    account_id: int | None
    chat_id: int
    created_at: datetime

class Membership(BaseModel):
    chat_id: int
    account_id: int

#Models for body parameters
class ChatCreate(BaseModel):
    name: str
    owner_id: int

class ChatUpdate(BaseModel):
    name: str | None = None
    owner_id: int | None = None

class MessageCreate(BaseModel):
    text: str
    account_id: int

class MessageUpdate(BaseModel):
    text: str

class MembershipCreate(BaseModel):
    account_id: int

#Models for auth

class Registration(BaseModel):
    username: str
    email: str
    password: str

class Login(BaseModel):
    username: str
    password: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class Claims(BaseModel):
    sub: str
    iss: str
    iat: int
    exp: int


