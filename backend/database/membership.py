from sqlmodel import Session, select
from backend.database.schema import DBChatMembership, DBChat, DBAccount, DBMessage
from backend.exceptions import EntityNotFound, ChatMembershipRequired, ChatOwnerRemoval
from backend.models import MembershipCreate


def add_membership(session: Session, chat_id: int, membership_create: MembershipCreate) -> tuple[DBChatMembership, bool]:
    """Add an account to a chat, or return existing membership."""

    chat = session.get(DBChat, chat_id)
    if not chat:
        raise EntityNotFound("chat", chat_id)

    account = session.get(DBAccount, membership_create.account_id)
    if not account:
        raise EntityNotFound("account", membership_create.account_id)

    # ✅ Check if membership already exists INSIDE the repository
    existing_membership = session.exec(
        select(DBChatMembership).where(
            (DBChatMembership.account_id == membership_create.account_id) &
            (DBChatMembership.chat_id == chat_id)
        )
    ).first()

    if existing_membership:
        return existing_membership, False  # ✅ Return membership with False (no new creation)

    # ✅ Create a new membership
    new_membership = DBChatMembership(account_id=membership_create.account_id, chat_id=chat_id)
    session.add(new_membership)
    session.commit()
    session.refresh(new_membership)

    return new_membership, True  # ✅


def remove_membership(session: Session, chat_id: int, account_id: int):
    """Remove an account from a chat and nullify their messages' account_id."""

    chat = session.get(DBChat, chat_id)
    if not chat:
        raise EntityNotFound("chat", chat_id)

    membership = session.exec(
        select(DBChatMembership).where(
            (DBChatMembership.account_id == account_id) &
            (DBChatMembership.chat_id == chat_id)
        )
    ).first()

    if not membership:
        raise ChatMembershipRequired(account_id, chat_id)

    if chat.owner_id == account_id:
        raise ChatOwnerRemoval()

    # ✅ Nullify account_id for all messages in this chat
    session.exec(
        select(DBMessage)
        .where((DBMessage.chat_id == chat_id) & (DBMessage.account_id == account_id))
        .update({DBMessage.account_id: None})
    )

    # ✅ Remove membership
    session.delete(membership)
    session.commit()