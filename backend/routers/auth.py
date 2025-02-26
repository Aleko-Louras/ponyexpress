from ctypes.wintypes import tagPOINT
from sys import prefix

from fastapi import APIRouter, Depends, Response, Form
from typing import Annotated
from sqlmodel import Session

from backend.database.schema import DBAccount
from backend.dependencies import DBSession, get_current_user
from backend.database.account import UserService
from backend.database.auth_service import AuthService
from backend.models import Registration, Login, AccessToken

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/registration", status_code=201)
def register_user(
    session: DBSession,
    form: Annotated[Registration, Form()]  # ✅ Form() is only used here
):
    user = UserService.register_user(session, form)
    return {"id": user.id, "username": user.username, "email": user.email}

@router.post("/token")
def login_user(
    session: DBSession,
    form: Annotated[Login, Form()]
):
    user = UserService.validate_credentials(session, form.username, form.password)
    return AccessToken(access_token=AuthService.create_access_token(user.id), token_type="bearer")

@router.post("/web/login", status_code=204)
def web_login(
    response: Response,
    session: DBSession,
    form: Annotated[Login, Form()]
):
    """Login and store JWT token in an HTTP-only cookie."""
    user = UserService.validate_credentials(session, form.username, form.password)
    response = Response(status_code=204)  # ✅ Create a Response with 204 status
    response.set_cookie(key="pony_express_token", value=AuthService.create_access_token(user.id), httponly=True)
    return response
@router.post("/web/logout", status_code=204)
def web_logout(response: Response, user: DBAccount = Depends(get_current_user)):
    """Logout a logged-in user by deleting the authentication cookie."""
    response = Response(status_code=204)  # ✅ Create a Response with 204 status
    response.delete_cookie("pony_express_token")
    return response