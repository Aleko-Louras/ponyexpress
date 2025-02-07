from fastapi import APIRouter
from starlette.responses import JSONResponse

from backend.database import membership as MembershipRepository
from backend.dependencies import DBSession
from backend.models import MembershipCreate, Membership

router = APIRouter(prefix="/chats", tags=["Memberships"])

@router.post("/{chat_id}/accounts", response_model=Membership)
def add_membership(chat_id: int, membership_create: MembershipCreate, session: DBSession):
        membership, is_new = MembershipRepository.add_membership(session, chat_id, membership_create)
        #return a tuble with membership and true
        #if the bool is false, the membership already exists, true if it was created
        status_code = 201 if is_new else 200
        return JSONResponse(status_code=status_code, content={"chat_id": chat_id, "account_id": membership_create.account_id})

@router.delete("/{chat_id}/accounts/{account_id}", status_code=204)
def remove_membership(chat_id: int, account_id: int, session: DBSession):
        MembershipRepository.remove_membership(session, chat_id, account_id)
        return