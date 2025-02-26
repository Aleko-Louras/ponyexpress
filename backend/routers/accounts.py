from fastapi import APIRouter, Depends, Form
from backend.database import account as AccountRepository
from backend.database.schema import DBAccount
from backend.dependencies import DBSession, get_current_user
from backend.models import Account, AccountWithEmail, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("/")
def get_accounts(session: DBSession) -> dict:
    accounts = AccountRepository.get_all_accounts(session)
    if not accounts:
        return {"metadata": {"count": 0}, "accounts": []}
    accounts_data = [Account(id=acc.id, username=acc.username) for acc in accounts]
    return {"metadata": {"count": len(accounts_data)}, "accounts": accounts_data}

@router.get("/me", response_model=AccountWithEmail, status_code=200)
def get_current_account(user: DBAccount = Depends(get_current_user)) -> AccountWithEmail:
    return AccountWithEmail(id=user.id, username=user.username, email= user.email)

@router.get("/{account_id}", response_model=Account)
def get_account(account_id: int, session: DBSession) -> DBAccount:
    account = AccountRepository.get_account_by_id(session, account_id)
    return account


@router.put("/me")
def update_current_account(
    account_update: AccountUpdate,
    session: DBSession,
    user: DBAccount = Depends(get_current_user),
):
    updated_account = AccountRepository.update_account(session, user.id, account_update.username, account_update.email)
    return {
        "id": updated_account.id,
        "username": updated_account.username,
        "email": updated_account.email,
    }

@router.put("/me/password", status_code=204)
def update_password(
    session: DBSession,
    user: DBAccount = Depends(get_current_user),
    old_password: str = Form(...),
    new_password: str = Form(...)
):
    AccountRepository.update_password(session, user.id, old_password, new_password)

@router.delete("/me", status_code=204)
def delete_current_account(session: DBSession, user: DBAccount = Depends(get_current_user)):
    AccountRepository.delete_account(session, user.id)


