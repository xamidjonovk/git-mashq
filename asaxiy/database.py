import os
from sqlmodel import Session, create_engine

from asaxiy.config import Settings


def make_engine(url: str | None = None):
    database_url = url or Settings().database_url
    if not database_url:
        raise RuntimeError("DATABASE_URL .env yoki muhitda berilmagan")
    return create_engine(database_url, pool_pre_ping=True)

def make_session(engine):
    return Session(engine, expire_on_commit=False)