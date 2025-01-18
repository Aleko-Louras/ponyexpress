"""PonyExpress backend API application.

Args:
    app (FastAPI): The FastAPI application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.dependencies import create_db_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(
    title="<your API title>",
    summary="<your API summary>",
    lifespan=lifespan,
)


@app.get("/status", response_model=None, status_code=204)
def status():
    pass
