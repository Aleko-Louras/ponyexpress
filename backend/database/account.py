from sqlmodel import Session, select
import backend.database.auth_service as AuthService
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
    """Update the username and/or email of an account.

    Args:
        session (Session): The database session.
        account_id (int): The id of the account to update.
        username (str | None): The new username (optional).
        email (str | None): The new email (optional).

    Returns:
        DBAccount: The updated account object.

    Raises:
        EntityNotFound: If no account with the given id exists.
        DuplicateEntityValue: If the new username or email is already taken by another account.
    """
    account = session.get(DBAccount, account_id)
    if not account:
        raise EntityNotFound("account", account_id)
    if username:
        existing_username = session.exec(select(DBAccount).where(DBAccount.username == username)).first()
        if existing_username and existing_username.id != account_id:
            raise DuplicateEntityValue("account", "username", username)
        account.username = username
    if email:
        existing_email = session.exec(select(DBAccount).where(DBAccount.email == email)).first()
        if existing_email and existing_email.id != account_id:  # ✅ Prevent duplicate, allow same email
            raise DuplicateEntityValue("account", "email", email)
        account.email = email

    session.commit()
    session.refresh(account)
    return account

def update_password(session: Session, account_id: int, old_password: str, new_password: str):
    """Update the password of an account.

        Args:
            session (Session): The database session.
            account_id (int): The id of the account whose password is being updated.
            old_password (str): The current password.
            new_password (str): The new password.

        Raises:
            EntityNotFound: If no account with the given id exists.
            InvalidCredentials: If the old password does not match the stored password.
    """
    account = session.get(DBAccount, account_id)
    if not account:
        raise EntityNotFound("account", account_id)
    if not AuthService.verify_password(old_password, account.hashed_password):
        raise InvalidCredentials()

    account.hashed_password = AuthService.hash_password(new_password)
    session.commit()

def delete_account(session: Session, account_id: int):
    """Delete an account.

    Args:
        session (Session): The database session.
        account_id (int): The id of the account to delete.

    Raises:
        EntityNotFound: If no account with the given id exists.
        ChatOwnerRemoval: If the account is the owner of any chats.
    """
    account = session.get(DBAccount, account_id)
    if not account:
        raise EntityNotFound("account", account_id)
    if session.exec(select(DBChat).where(DBChat.owner_id == account_id)).first():
        raise ChatOwnerRemoval()

    session.delete(account)
    session.commit()


def register_user(session: Session, form: Registration) -> DBAccount:
    """Register a new user account.

    Args:
        session (Session): The database session.
        form (Registration): The registration form data.

    Returns:
        DBAccount: The newly created user account.

    Raises:
        DuplicateEntityValue: If the username or email already exists.
    """

    if session.exec(select(DBAccount).where(DBAccount.username == form.username)).first():
        raise DuplicateEntityValue("account", "username", form.username)

    if session.exec(select(DBAccount).where(DBAccount.email == form.email)).first():
        raise DuplicateEntityValue("account", "email", form.email)

    hashed_password = AuthService.hash_password(form.password)
    user = DBAccount(username=form.username, email=form.email, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def validate_credentials(session: Session, username: str, password: str) -> DBAccount:
    """Validate user credentials.

        Args:
            session (Session): The database session.
            username (str): The username of the account.
            password (str): The password of the account.

        Returns:
            DBAccount: The authenticated account.

        Raises:
            InvalidCredentials: If the username or password is incorrect.
    """
    user = session.exec(select(DBAccount).where(DBAccount.username == username)).first()
    if user is None or not AuthService.verify_password(password, user.hashed_password):
        raise InvalidCredentials()
    return user

def get_user_by_id(session: Session, user_id: int) -> DBAccount:
    """Retrieve a user by their account ID.

        Args:
            session (Session): The database session.
            user_id (int): The id of the user to retrieve.

        Returns:
            DBAccount: The user account.

        Raises:
            EntityNotFound: If no user with the given id exists.
        """
    user = session.get(DBAccount, user_id)
    if user is None:
        raise EntityNotFound("account", user_id)
    return user
