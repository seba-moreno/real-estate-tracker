from __future__ import annotations

from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


SQLALCHEMY_DB_URL = (
    "sqlite:///C:/Users/smorenocam001/Downloads/real-estate-tracker/src/database.db"
)

engine: Engine = create_engine(
    SQLALCHEMY_DB_URL,
    future=True,
    connect_args={"check_same_thread": False},
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
