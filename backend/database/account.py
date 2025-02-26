from fastapi import HTTPException
from sqlmodel import Session, select
from backend.database.auth_service import AuthService
from backend.models import Registration
from backend.database.schema import DBAccount, DBChat
from backend.exceptions import EntityNotFound, DuplicateEntityValue, InvalidCredentials, ChatOwnerRemoval


def get_all_accounts(session: Session) -> list[DBAccount]:
    """Select all the accounts from the database

    Args:
        session (Session): The database session

    Returns:
        list[DBAccount]: The list of accounts
    """
    stmt = select(DBAccount).order_by(DBAccount.id)
    results = session.exec(stmt)
    return list(results)

def get_account_by_id(session: Session, account_id: int) -> DBAccount:
    """Selects the account by id in the database

    Args:
        session (Session): The database session
        account_id (int): The id of the account to get

    Returns:
        DBAccount: The account

    Raises:
        EntityNotFound: If no account with the given id exists
    """
    account = session.get(DBAccount, account_id)
    if account is None:
        raise EntityNotFound("account", account_id)
    return account

def update_account(session: Session, account_id: int, username: str | None = None, email: str | None = None) -> DBAccount:
    """Update the username and/or email of an account."""
    account = session.get(DBAccount, account_id)
    if not account:
        raise EntityNotFound("account", account_id)

    # Update username if provided
    if username:
        existing_username = session.exec(select(DBAccount).where(DBAccount.username == username)).first()
        if existing_username and existing_username.id != account_id:
            raise DuplicateEntityValue("account", "username", username)
        account.username = username

    # Update email if provided
    if email:
        existing_email = session.exec(select(DBAccount).where(DBAccount.email == email)).first()
        if existing_email and existing_email.id != account_id:
            raise DuplicateEntityValue("account", "email", email)
        account.email = email

    session.commit()
    session.refresh(account)
    return account

def update_password(session: Session, account_id: int, old_password: str, new_password: str):
    """Update the password of an account."""
    account = session.get(DBAccount, account_id)
    if not account:
        raise EntityNotFound("account", account_id)

    # Verify the old password
    if not AuthService.verify_password(old_password, account.hashed_password):
        raise ValueError("invalid_credentials")

    # Hash the new password and update
    account.hashed_password = AuthService.hash_password(new_password)
    session.commit()

def delete_account(session: Session, account_id: int):
    """Delete an account. Raises ChatOwnerRemoval if the account owns any chats."""
    account = session.get(DBAccount, account_id)
    if not account:
        raise EntityNotFound("account", account_id)

    # ✅ Check if the account is the owner of any chats
    if session.exec(select(DBChat).where(DBChat.owner_id == account_id)).first():
        raise ChatOwnerRemoval()

    session.delete(account)
    session.commit()

class UserService:
    @staticmethod
    def register_user(session: Session, form: Registration) -> DBAccount:
        """Register a new user account."""

        # Duplicate username
        if session.exec(select(DBAccount).where(DBAccount.username == form.username)).first():
            raise DuplicateEntityValue("account", "username", form.username)

        # Duplicate email
        if session.exec(select(DBAccount).where(DBAccount.email == form.email)).first():
            raise DuplicateEntityValue("account", "email", form.email)

        # Create user
        hashed_password = AuthService.hash_password(form.password)
        user = DBAccount(username=form.username, email=form.email, hashed_password=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def validate_credentials(session: Session, username: str, password: str) -> DBAccount:
        """Validate user credentials and return the user if valid."""
        user = session.exec(select(DBAccount).where(DBAccount.username == username)).first()
        if user is None or not AuthService.verify_password(password, user.hashed_password):
            raise InvalidCredentials()  # ✅ Custom exception with no "detail" wrapper
        return user
    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> DBAccount:
        user = session.get(DBAccount, user_id)
        if user is None:
            raise EntityNotFound("account", user_id)
        return user
