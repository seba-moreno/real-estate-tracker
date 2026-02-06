from __future__ import annotations

import os
import sys
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


SQLALCHEMY_DB_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DB_URL:
    print("Error: DATABASE_URL environment variable is not set.")
    sys.exit(1)

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
