from fastapi import APIRouter, Depends, HTTPException
from backend.database import membership as MembershipRepository
from backend.dependencies import DBSession
from backend.models import MembershipCreate, Membership
from backend.exceptions import EntityNotFound, ChatMembershipRequired, ChatOwnerRemoval

router = APIRouter(prefix="/chats", tags=["Memberships"])


@router.post("/{chat_id}/accounts", response_model=Membership)
def add_membership(chat_id: int, membership_create: MembershipCreate, session: DBSession):
    try:
        return MembershipRepository.add_membership(session, chat_id, membership_create)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail={"error": e.error, "message": e.message})


@router.delete("/{chat_id}/accounts/{account_id}", status_code=204)
def remove_membership(chat_id: int, account_id: int, session: DBSession):
    try:
        MembershipRepository.remove_membership(session, chat_id, account_id)
        return
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail={"error": e.error, "message": e.message})
    except ChatMembershipRequired as e:
        raise HTTPException(status_code=422, detail={"error": e.error, "message": e.message})
    except ChatOwnerRemoval as e:
        raise HTTPException(status_code=422, detail={"error": e.error, "message": e.message})