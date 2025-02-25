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

@router.get("/me", response_model=Account)
def get_current_account(user: DBAccount = Depends(get_current_user)) -> Account:
    """Retrieve the account data of the authenticated user."""
    return Account(id=user.id, username=user.username)

@router.put("/me")
def update_current_account(session: DBSession, user: DBAccount = Depends(get_current_user), username: str | None = None, email: str | None = None):
    """Update the authenticated user's account."""
    return AccountRepository.update_account(session, user.id, username, email)

@router.put("/me/password", status_code=204)
def update_password(session: DBSession, old_password: str, new_password: str, user: DBAccount = Depends(get_current_user)):
    """Update the authenticated user's password."""
    AccountRepository.update_password(session, user.id, old_password, new_password)

@router.delete("/me", status_code=204)
def delete_current_account(session: DBSession, user: DBAccount = Depends(get_current_user)):
    """Delete the authenticated user's account."""
    AccountRepository.delete_account(session, user.id)


