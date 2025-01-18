"""Database table models."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class DBAccount(SQLModel, table=True):
    __tablename__ = "accounts"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    hashed_password: str


class DBChat(SQLModel, table=True):
    __tablename__ = "chats"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str
    owner_id: int = Field(foreign_key="accounts.id")


class DBMessage(SQLModel, table=True):
    __tablename__ = "messages"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    text: str
    account_id: int = Field(foreign_key="accounts.id")
    chat_id: int = Field(foreign_key="chats.id")
    created_at: datetime | None = Field(default_factory=datetime.now)


class DBChatMembership(SQLModel, table=True):
    __tablename__ = "chat_memberships"  # type: ignore

    account_id: int = Field(foreign_key="accounts.id", primary_key=True)
    chat_id: int = Field(foreign_key="chats.id", primary_key=True)
