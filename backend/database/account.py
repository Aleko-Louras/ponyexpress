from sqlmodel import Session, select

from backend.database.schema import DBAccount
from backend.exceptions import EntityNotFound

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