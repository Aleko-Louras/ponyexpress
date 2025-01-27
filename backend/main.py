"""PonyExpress backend API application.

Args:
    app (FastAPI): The FastAPI application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.dependencies import create_db_tables
from backend.exceptions import EntityNotFound
from backend.routers import accounts, chats

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield

app = FastAPI(
    title="Pony Express",
    summary="A chat application",
    lifespan=lifespan,
)

@app.exception_handler(EntityNotFound)
def handle_entity_not_found(request: Request, exc: EntityNotFound):
    return JSONResponse(
        status_code=404,
        content={
            "error": exc.error,
            "message": exc.message,
        },
    )
app.include_router(accounts.router)
app.include_router(chats.router)

@app.get("/status", response_model=None, status_code=204)
def status():
    pass

