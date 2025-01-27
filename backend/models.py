from pydantic import BaseModel
from datetime import datetime

class Metadata(BaseModel):
    count: int

class Account(BaseModel):
    id: int
    username: str

class Chat(BaseModel):
    id: int
    name: str
    owner_id: int

class Message(BaseModel):
    id: int
    text: str
    account_id: int
    chat_id: int
    created_at: datetime
