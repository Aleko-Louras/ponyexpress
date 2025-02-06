from sqlmodel import Session, select
from backend.database.schema import DBChat, DBMessage, DBAccount, DBChatMembership
from backend.exceptions import EntityNotFound
from backend.models import ChatCreate


def create_chat(session: Session, chat_create: ChatCreate) -> DBChat:
    if not session.get(DBAccount, chat_create.owner_id):
        raise EntityNotFound("account", chat_create.owner_id)

    if session.exec(select(DBChat).where(DBChat.name == chat_create.name)).first():
        raise IntegrityError(f"Duplicat")
def get_all_chats(session: Session) -> list[DBChat]:
    """Retrieve all chats from the database.

    Args:
        session (Session): The database session

    Returns:
        list[DBChat]: The list of chats
    """
    stmt = select(DBChat).order_by(DBChat.id)
    results = session.exec(stmt)
    return list(results)

def get_chat_by_id(session: Session, chat_id: int) -> DBChat:
    """Retrieve a specific chat from the database.

    Args:
        session (Session): The database session
        chat_id (int): The id of the chat to retrieve

    Returns:
        DBChat: The chat

    Raises:
        EntityNotFound: If no chat with the given id exists
    """
    chat = session.get(DBChat, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    return chat

def get_messages_by_chat_id(session: Session, chat_id: int) -> list[DBMessage]:
    """Retrieve all messages for a specific chat from the database.

    Args:
        session (Session): The database session
        chat_id (int): The id of the chat whose messages are to be retrieved

    Returns:
        list[DBMessage]: The list of messages
    """
    chat = session.get(DBChat, chat_id)
    if not chat:
        raise EntityNotFound("chat", chat_id)
    stmt = select(DBMessage).where(DBMessage.chat_id == chat_id).order_by(DBMessage.id)
    results = session.exec(stmt).all()
    return results

def get_accounts_by_chat_id(session: Session, chat_id: int) -> list[DBAccount]:
    """Retrieve all accounts for a specific chat.

    Args:
        session (Session): The database session
        chat_id (int): The id of the chat

    Returns:
        list[DBAccount]: The list of accounts
    """
    stmt = select(DBChatMembership).where(DBChatMembership.chat_id == chat_id)
    memberships = session.exec(stmt).all()
    if not memberships:
        raise EntityNotFound("chat", chat_id)
    account_ids = [membership.account_id for membership in memberships]
    stmt = select(DBAccount).where(DBAccount.id.in_(account_ids)).order_by(DBAccount.id)
    results = session.exec(stmt).all()
    return results