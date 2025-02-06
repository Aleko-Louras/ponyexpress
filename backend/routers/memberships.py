from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from backend.database import membership as MembershipRepository
from backend.database.schema import DBChatMembership
from backend.dependencies import DBSession
from backend.models import MembershipCreate, Membership
from backend.exceptions import EntityNotFound, ChatMembershipRequired, ChatOwnerRemoval

router = APIRouter(prefix="/chats", tags=["Memberships"])


# @router.post("/{chat_id}/accounts", response_model=Membership)
# def add_membership(chat_id: int, membership_create: MembershipCreate, session: DBSession):
#     try:
#         return MembershipRepository.add_membership(session, chat_id, membership_create)
#     except EntityNotFound as e:
#         raise HTTPException(status_code=404, detail={"error": e.error, "message": e.message})

@router.post("/{chat_id}/accounts", response_model=Membership)
def add_membership(chat_id: int, membership_create: MembershipCreate, session: DBSession):
    try:
        membership = MembershipRepository.add_membership(session, chat_id, membership_create)

        # ✅ Return 201 if a new membership was created, otherwise 200
        status_code = 201 if session.get(DBChatMembership, (membership_create.account_id, chat_id)) is None else 200

        return JSONResponse(
            status_code=status_code,
            content={"chat_id": chat_id, "account_id": membership_create.account_id}
        )
    except EntityNotFound as e:
        raise e  # ✅ Keep error handling consistent

@router.delete("/{chat_id}/accounts/{account_id}", status_code=204)
def remove_membership(chat_id: int, account_id: int, session: DBSession):
    try:
        MembershipRepository.remove_membership(session, chat_id, account_id)
        return
    except EntityNotFound as e:
        raise e  # ✅ Raise it directly (so it goes through the custom handler)
    except ChatMembershipRequired as e:
        raise e  # ✅ Raise it directly
    except ChatOwnerRemoval as e:
        raise e  # ✅ Raise it directly, FastAPI will handle it!