"""SQLAlchemy engine, session factory and Base."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

# check_same_thread=False is required for SQLite when used by FastAPI's threadpool.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Create tables if they do not yet exist."""
    # Import models so they are registered on Base.metadata before create_all.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency yielding a DB session and ensuring it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
