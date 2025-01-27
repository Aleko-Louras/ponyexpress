from fastapi import APIRouter
from backend.database import account as AccountRepository
from backend.database.schema import DBAccount
from backend.dependencies import DBSession
from backend.models import Account

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("/")
def get_accounts(session: DBSession) -> dict:
    accounts = AccountRepository.get_all_accounts(session)
    if not accounts:
        return {"metadata": {"count": 0}, "accounts": []}
    accounts_data = [Account(id=acc.id, username=acc.username) for acc in accounts]
    return {"metadata": {"count": len(accounts_data)}, "accounts": accounts_data}

@router.get("/{account_id}", response_model=Account)
def get_account(account_id: int, session: DBSession) -> DBAccount:
    account = AccountRepository.get_account_by_id(session, account_id)
    return account

