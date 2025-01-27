"""PonyExpress backend API application.

Args:
    app (FastAPI): The FastAPI application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.dependencies import create_db_tables
#import separate router modules
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
app.include_router(accounts.router)
app.include_router(chats.router)

# @app.get("/status", response_model=None, status_code=204)
# def status():
#     pass
#
