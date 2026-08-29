"""
SQLAlchemy engine/session setup.

Uses SQLite for local development. Because the connection string and models
use standard SQLAlchemy (no SQLite-only features), moving to MySQL only
requires changing DATABASE_URL, e.g.:

    DATABASE_URL=mysql+pymysql://user:password@host:3306/forgeguard

and installing `pymysql` (add to requirements.txt).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
