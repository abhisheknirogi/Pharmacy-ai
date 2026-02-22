"""
Database configuration and session management.
Provides SQLAlchemy engine, session factory, and dependency injection.
"""

import os
import logging
from typing import Generator
from sqlalchemy import create_engine, Engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool

from .config import settings

logger = logging.getLogger(__name__)

# Database path setup
DB_PATH = os.path.join(os.path.dirname(__file__), "../../pharmacy.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create engine with appropriate pool
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    # SQLite configuration
    engine: Engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL/MySQL configuration with connection pooling
    engine: Engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_POOL_MAX_OVERFLOW,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        echo=settings.DEBUG,
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record) -> None:
    """Enable foreign keys and other pragmas for SQLite."""
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get DB session.
    Ensures proper cleanup after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database - create all tables.
    Call this during application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def close_db() -> None:
    """Close database connection. Call during application shutdown."""
    try:
        engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")