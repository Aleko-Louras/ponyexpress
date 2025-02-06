from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from backend.database import membership as MembershipRepository
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
        new_membership = MembershipRepository.add_membership(session, chat_id, membership_create)
        status_code = 201 if new_membership else 200  # ✅ Return 201 if new membership is created
        return JSONResponse(status_code=status_code, content=new_membership.dict())
    except EntityNotFound as e:
        raise e

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