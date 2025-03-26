from fastapi import APIRouter, Depends, Response, Form
from typing import Annotated

import backend.database.account
from backend.database.schema import DBAccount
from backend.dependencies import DBSession, get_current_user
from backend.database.account import validate_credentials
import backend.database.auth_service as AuthService
from backend.models import Registration, Login, AccessToken

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/registration", status_code=201)
def register_user(
    session: DBSession,
    form: Annotated[Registration, Form()]
):
    user = backend.database.account.register_user(session, form)
    return {"id": user.id, "username": user.username, "email": user.email}

@router.post("/token")
def login_user(
    session: DBSession,
    form: Annotated[Login, Form()]
):
    user = validate_credentials(session, form.username, form.password)
    return AccessToken(access_token=AuthService.create_access_token(user.id), token_type="bearer")

@router.post("/web/login", status_code=204)
def web_login(
    session: DBSession,
    form: Annotated[Login, Form()]
):
    user = validate_credentials(session, form.username, form.password)
    response = Response(status_code=204)
    response.set_cookie(key="pony_express_token", value=AuthService.create_access_token(user.id), httponly=True)
    return response
@router.post("/web/logout", status_code=204)
def web_logout(response: Response, user: DBAccount = Depends(get_current_user)):
    response = Response(status_code=204)
    response.delete_cookie("pony_express_token")
    return response