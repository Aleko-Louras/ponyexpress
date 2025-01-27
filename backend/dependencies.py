"""Dependencies for the backend API.

Args:
    engine (sqlachemy.engine.Engine): The database engine
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated
from backend.database.schema import *
from fastapi import Depends


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
