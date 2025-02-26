"""Dependencies for the backend API.

Args:
    engine (sqlachemy.engine.Engine): The database engine
"""
from fastapi.security import APIKeyCookie, HTTPBearer
from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated

from backend.database.account import UserService
from backend.database.auth_service import AuthService
from backend.database.schema import *
from fastapi import Depends, HTTPException

from backend.exceptions import AuthenticationRequired, InvalidAccessToken, ExpiredAccessToken

_db_filename = "backend/database/development.db"
_db_url = f"sqlite:///{_db_filename}"
connect_args = {"check_same_thread": False}
engine = create_engine(_db_url, echo=True, connect_args=connect_args)


def create_db_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


DBSession = Annotated[Session, Depends(get_session)]

cookie_scheme = APIKeyCookie(name="pony_express_token", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def get_access_token(
    cookie_token: str | None = Depends(cookie_scheme),
    bearer_token: str | None = Depends(bearer_scheme)
) -> str:
    """Retrieve JWT from Authorization header or HTTP-only cookie."""
    if cookie_token:
        return cookie_token
    if bearer_token:
        return bearer_token.credentials
    raise AuthenticationRequired()


def get_current_user(session: DBSession, token: str = Depends(get_access_token)) -> DBAccount:
    """Authenticate the user using JWT and return the DBAccount."""
    try:
        payload = AuthService.decode_access_token(token)
        user_id = int(payload["sub"])
        user = UserService.get_user_by_id(session, user_id)
        if user is None:
            raise AuthenticationRequired()  # ✅ No user found, raise custom exception
        return user

    except ValueError as error:
        error_message = str(error)
        if error_message == "expired_access_token":
            raise ExpiredAccessToken()
        elif error_message == "invalid_access_token":
            raise InvalidAccessToken()
        elif error_message == "authentication_required":
            raise AuthenticationRequired()