from fastapi import APIRouter, Depends, HTTPException
from backend.database import message as MessageRepository
from backend.database.schema import DBChat, DBMessage
from backend.dependencies import DBSession
from backend.models import MessageCreate, MessageUpdate, Message
from backend.exceptions import EntityNotFound, ChatMembershipRequired

router = APIRouter(prefix="/chats", tags=["Messages"])


@router.post("/{chat_id}/messages", response_model=Message, status_code=201)
def create_message(chat_id: int, message_create: MessageCreate, session: DBSession):
    try:
        return MessageRepository.create_message(session, chat_id, message_create)
    except EntityNotFound as e:
        raise e
    except ChatMembershipRequired as e:
        raise e


@router.put("/{chat_id}/messages/{message_id}", response_model=Message)
def update_message(chat_id: int, message_id: int, message_update: MessageUpdate, session: DBSession):
    try:
        return MessageRepository.update_message(session, chat_id, message_id, message_update)
    except EntityNotFound as e:
        raise e


@router.delete("/{chat_id}/messages/{message_id}", status_code=204)
def delete_message(chat_id: int, message_id: int, session: DBSession):
    try:
        # ✅ First, check if the chat exists
        chat = session.get(DBChat, chat_id)
        if chat is None:
            raise EntityNotFound("chat", chat_id)  # ✅ Raises correct error first

        # ✅ Then check if the message exists
        message = session.get(DBMessage, message_id)
        if message is None or message.chat_id != chat_id:
            raise EntityNotFound("message", message_id)  # ✅ Only raise message error if chat exists

        session.delete(message)
        session.commit()

        return
    except EntityNotFound as e:
        raise e