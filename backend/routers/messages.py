from fastapi import APIRouter, Depends, HTTPException
from backend.database import message as MessageRepository
from backend.database.schema import DBChat, DBMessage, DBAccount
from backend.dependencies import DBSession, get_current_user
from backend.models import MessageCreate, MessageUpdate, Message
from backend.exceptions import EntityNotFound, ChatMembershipRequired, AccessDenied

router = APIRouter(prefix="/chats", tags=["Messages"])


@router.post("/{chat_id}/messages", response_model=Message, status_code=201)
def create_message(chat_id: int, message_create: MessageCreate, session: DBSession, user: DBAccount = Depends(get_current_user)):
    """Create a new message in a chat - User must match the account_id."""
    if user.id != message_create.account_id:
        raise AccessDenied()
    return MessageRepository.create_message(session, chat_id, message_create)

@router.put("/{chat_id}/messages/{message_id}", response_model=Message)
def update_message(chat_id: int, message_id: int, message_update: MessageUpdate, session: DBSession):
    return MessageRepository.update_message(session, chat_id, message_id, message_update)

@router.delete("/{chat_id}/messages/{message_id}", status_code=204)
def delete_message(chat_id: int, message_id: int, session: DBSession):
    MessageRepository.delete_message(session, chat_id, message_id)
    return