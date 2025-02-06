from sqlmodel import Session, select
from backend.database.schema import DBChatMembership, DBChat, DBAccount
from backend.exceptions import EntityNotFound, ChatMembershipRequired, ChatOwnerRemoval
from backend.models import MembershipCreate


def add_membership(session: Session, chat_id: int, membership_create: MembershipCreate) -> DBChatMembership:
    """Add an account to a chat."""
    chat = session.get(DBChat, chat_id)
    if not chat:
        raise EntityNotFound("chat", chat_id)

    account = session.get(DBAccount, membership_create.account_id)
    if not account:
        raise EntityNotFound("account", membership_create.account_id)

    existing_membership = session.exec(
        select(DBChatMembership).where(
            (DBChatMembership.account_id == membership_create.account_id) & (DBChatMembership.chat_id == chat_id)
        )
    ).first()

    if existing_membership:
        return existing_membership  # No need to add if already a member

    new_membership = DBChatMembership(account_id=membership_create.account_id, chat_id=chat_id)
    session.add(new_membership)
    session.commit()
    return new_membership


def remove_membership(session: Session, chat_id: int, account_id: int):
    """Remove an account from a chat."""
    chat = session.get(DBChat, chat_id)
    if not chat:
        raise EntityNotFound("chat", chat_id)

    membership = session.exec(
        select(DBChatMembership).where(
            (DBChatMembership.account_id == account_id) & (DBChatMembership.chat_id == chat_id)
        )
    ).first()

    if not membership:
        raise ChatMembershipRequired(account_id, chat_id)

    if chat.owner_id == account_id:
        raise ChatOwnerRemoval()

    session.delete(membership)
    session.commit()