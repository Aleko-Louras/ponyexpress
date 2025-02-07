from sqlmodel import Session, select
from backend.database.schema import DBChatMembership, DBChat, DBAccount, DBMessage
from backend.exceptions import EntityNotFound, ChatMembershipRequired, ChatOwnerRemoval
from backend.models import MembershipCreate


def add_membership(session: Session, chat_id: int, membership_create: MembershipCreate) -> tuple[DBChatMembership, bool]:
    """Add an account to a chat or return existing membership.

        Args:
            session (Session): The database session
            chat_id (int): The ID of the chat to which the account should be added
            membership_create (MembershipCreate): The data model containing the account ID

        Returns:
            tuple[DBChatMembership, bool]: The chat membership entity representing the association between the account and the chat, true/false,
            depending on if the membership was created or already existed
    """
    chat = session.get(DBChat, chat_id)
    if not chat:
        raise EntityNotFound("chat", chat_id)

    account = session.get(DBAccount, membership_create.account_id)
    if not account:
        raise EntityNotFound("account", membership_create.account_id)

    existing_membership = session.exec(select(DBChatMembership).where((DBChatMembership.account_id == membership_create.account_id) & (DBChatMembership.chat_id == chat_id))).first()
    if existing_membership:
        return existing_membership, False #no membership was created, it existed

    new_membership = DBChatMembership(account_id=membership_create.account_id, chat_id=chat_id)
    session.add(new_membership)
    session.commit()
    session.refresh(new_membership)

    return new_membership, True


def remove_membership(session: Session, chat_id: int, account_id: int):
    """Remove an account from a chat and nullify their messages' account_id.

        Args:
            session (Session): The database session
            chat_id (int): The ID of the chat from which the account should be removed
            account_id (int): The ID of the account to be removed from the chat

        Returns:
            None
    """
    chat = session.get(DBChat, chat_id)
    if not chat:
        raise EntityNotFound("chat", chat_id)

    membership = session.exec(select(DBChatMembership).where((DBChatMembership.account_id == account_id) & (DBChatMembership.chat_id == chat_id))).first()
    if not membership:
        raise ChatMembershipRequired(account_id, chat_id)

    if chat.owner_id == account_id:
        raise ChatOwnerRemoval()

    messages = session.exec(select(DBMessage).where((DBMessage.chat_id == chat_id) & (DBMessage.account_id == account_id))).all()
    for message in messages:
        message.account_id = None

    session.commit()
    session.delete(membership)
    session.commit()