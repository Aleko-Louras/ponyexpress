from fastapi import APIRouter, Depends, HTTPException
from backend.database import chat as ChatRepository
from backend.database.schema import DBChat
from backend.dependencies import DBSession
from backend.exceptions import EntityNotFound, DuplicateEntityValue, ChatMembershipRequired
from backend.models import Chat, Metadata, Account, Message, ChatCreate, ChatUpdate
from typing import List

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("/", response_model=Chat, status_code=201)
def create_chat(chat_create: ChatCreate, session: DBSession):
    try:
        return ChatRepository.create_chat(session, chat_create)
    except EntityNotFound as e:
        raise e
    except DuplicateEntityValue as e:
        raise e

@router.put("/{chat_id}", response_model=Chat)
def update_chat(chat_id: int, chat_update: ChatUpdate, session: DBSession):
    try:
        return ChatRepository.update_chat(session, chat_id, chat_update)
    except EntityNotFound as e:
        raise e
    except DuplicateEntityValue as e:
        raise e
    except ChatMembershipRequired as e:
        raise e


@router.delete("/{chat_id}", status_code=204)
def delete_chat(chat_id: int, session: DBSession):
    try:
        ChatRepository.delete_chat(session, chat_id)
        return
    except EntityNotFound as e:
        raise e

@router.get("/")
def get_chats(session: DBSession) -> dict:
    chats = ChatRepository.get_all_chats(session)
    if not chats:
        return {"metadata": {"count": 0}, "chats": []}
    chats_data = [Chat(id=chat.id, name= chat.name, owner_id= chat.owner_id) for chat in chats]
    return {"metadata": {"count": len(chats_data)}, "chats": chats_data}

@router.get("/{chat_id}", response_model=Chat)
def get_chat(chat_id: int, session: DBSession)-> DBChat:
    chat = ChatRepository.get_chat_by_id(session, chat_id)
    return chat


@router.get("/{chat_id}/messages")
def get_chat_messages(chat_id: int, session: DBSession):
    messages = ChatRepository.get_messages_by_chat_id(session, chat_id)
    messages_data = [
        Message(
            id= msg.id,
            text= msg.text,
            account_id= msg.account_id,
            chat_id= msg.chat_id,
            created_at = msg.created_at.isoformat(),
    )
        for msg in messages
    ]
    return {"metadata": {"count": len(messages_data)}, "messages": messages_data}

@router.get("/{chat_id}/accounts", response_model=dict)
def get_chat_accounts(chat_id: int, session: DBSession):
    accounts = ChatRepository.get_accounts_by_chat_id(session, chat_id)
    accounts_data = [Account(id= acc.id, username= acc.username) for acc in accounts]
    return {
        "metadata": {"count": len(accounts_data)},
        "accounts": accounts_data,
    }