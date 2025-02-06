from sqlmodel import Session, select
from backend.database.schema import DBChat, DBMessage, DBAccount, DBChatMembership
from backend.exceptions import EntityNotFound, DuplicateEntityValue, ChatMembershipRequired
from backend.models import ChatCreate, ChatUpdate, MessageUpdate, MessageCreate


def create_chat(session: Session, chat_create: ChatCreate) -> DBChat:
    if not session.get(DBAccount, chat_create.owner_id):#if the account doesnt exists
        raise EntityNotFound("account", chat_create.owner_id)

    if session.exec(select(DBChat).where(DBChat.name == chat_create.name)).first():#if the chat exists already
        raise DuplicateEntityValue("chat", "name", chat_create.name)
    chat_to_add = DBChat(name=chat_create.name, owner_id=chat_create.owner_id)
    session.add(chat_to_add)
    session.commit()
    session.refresh(chat_to_add)

    new_membership = DBChatMembership(account_id = chat_to_add.owner_id, chat_id= chat_to_add.id)
    session.add(new_membership)
    session.commit()

    return chat_to_add

def update_chat(session: Session, chat_id: int, chat_update: ChatUpdate) -> DBChat:
    chat = session.get(DBChat, chat_id)
    if not chat:
        raise EntityNotFound("chat", chat_id)

    if chat_update.name:
        existing_chat = session.exec(select(DBChat).where(DBChat.name == chat_update.name)).first()
        if existing_chat and existing_chat.id != chat_id:
            raise DuplicateEntityValue("chat", "name", chat_update.name)
        chat.name = chat_update.name

    if chat_update.owner_id:
        owner = session.get(DBAccount, chat_update.owner_id)
        if not owner:
            raise EntityNotFound("account", chat_update.owner_id)
        if not session.exec(select(DBChatMembership).where((DBChatMembership.account_id == chat_update.owner_id) & (DBChatMembership.chat_id == chat_id))).first():
            raise ChatMembershipRequired(chat_update.owner_id, chat_id)
        chat.owner_id = chat_update.owner_id

    session.commit()
    session.refresh(chat)
    return chat

def delete_chat(session: Session, chat_id: int):
    chat_to_delete = session.get(DBChat, chat_id)
    if not chat_to_delete:
        raise EntityNotFound("chat", chat_id)
    session.delete(chat_to_delete)
    session.commit()

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
#message related db queries


