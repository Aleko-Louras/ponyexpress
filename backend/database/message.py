from sqlmodel import Session, select

from backend.database.schema import DBMessage, DBChat, DBAccount, DBChatMembership
from backend.exceptions import EntityNotFound, ChatMembershipRequired
from backend.models import MessageCreate, MessageUpdate


def create_message(session: Session, chat_id: int, message_create: MessageCreate) -> DBMessage:
    """Create a new message in a chat."""
    chat = session.get(DBChat, chat_id)
    if not chat:
        raise EntityNotFound("chat", chat_id)

    account = session.get(DBAccount, message_create.account_id)
    if not account:
        raise EntityNotFound("account", message_create.account_id)

    membership = session.exec(select(DBChatMembership).where((DBChatMembership.account_id == message_create.account_id) & (DBChatMembership.chat_id == chat_id))).first()
    if not membership:
        raise ChatMembershipRequired(message_create.account_id, chat_id)

    message = DBMessage(
        text=message_create.text,
        account_id=message_create.account_id,
        chat_id=chat_id
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def update_message(session: Session, chat_id: int, message_id: int, message_update: MessageUpdate) -> DBMessage:
    """Update a message's text."""
    message = session.get(DBMessage, message_id)
    if not message or message.chat_id != chat_id:
        raise EntityNotFound("message", message_id)

    message.text = message_update.text
    session.commit()
    session.refresh(message)
    return message


def delete_message(session: Session, chat_id: int, message_id: int):
    """Delete a message."""
    message = session.get(DBMessage, message_id)
    if not message or message.chat_id != chat_id:
        raise EntityNotFound("message", message_id)

    session.delete(message)
    session.commit()