"""PonyExpress backend API application.

Args:
    app (FastAPI): The FastAPI application
"""
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.dependencies import create_db_tables
from backend.exceptions import EntityNotFound, DuplicateEntityValue, ChatMembershipRequired, ChatOwnerRemoval, \
    InvalidCredentials, ExpiredAccessToken, AuthenticationRequired, InvalidAccessToken, AccessDenied
from backend.routers import accounts, chats, memberships, messages, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield

app = FastAPI(
    title="Pony Express",
    summary="A chat application",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

#Implementation for different exception types to raise and json to respond
@app.exception_handler(EntityNotFound)
def handle_entity_not_found(request: Request, exc: EntityNotFound):
    return JSONResponse(
        status_code=404,
        content={
            "error": exc.error,
            "message": exc.message,
        },
    )

@app.exception_handler(DuplicateEntityValue)
def handle_duplicate_entity_value(request: Request, exc: DuplicateEntityValue):
    return JSONResponse(
        status_code=422,
        content={"error": exc.error, "message": exc.message}
    )

@app.exception_handler(ChatMembershipRequired)
def handle_chat_membership_required(request: Request, exc: ChatMembershipRequired):
    return JSONResponse(
        status_code=422,
        content={"error": exc.error, "message": exc.message}
    )

@app.exception_handler(ChatOwnerRemoval)
def handle_chat_owner_removal(request: Request, exc: ChatOwnerRemoval):
    return JSONResponse(
        status_code=422,
        content={"error": exc.error, "message": exc.message}
    )
@app.exception_handler(InvalidCredentials)
def handle_invalid_credentials(request: Request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=401,
        content={"error": exc.error, "message": exc.message}
    )
@app.exception_handler(AuthenticationRequired)
def handle_authentication_required(request: Request, exc: AuthenticationRequired):
    return JSONResponse(
        status_code=403,
        content={"error": exc.error, "message": exc.message}
    )

@app.exception_handler(ExpiredAccessToken)
def handle_expired_access_token(request: Request, exc: ExpiredAccessToken):
    return JSONResponse(
        status_code=403,
        content={"error": exc.error, "message": exc.message}
    )

@app.exception_handler(InvalidAccessToken)
def handle_invalid_access_token(request: Request, exc: InvalidAccessToken):
    return JSONResponse(
        status_code=403,
        content={"error": exc.error, "message": exc.message}
    )
@app.exception_handler(AccessDenied)
def handle_access_denied(request: Request, exc: AccessDenied):
    return JSONResponse(
        status_code=403,
        content={"error": exc.error, "message": exc.message}
    )

app.include_router(accounts.router)
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(memberships.router)
app.include_router(auth.router)

@app.get("/status", response_model=None, status_code=204)
def status():
    pass

