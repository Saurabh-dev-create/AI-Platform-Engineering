from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.connection import engine


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Provide one database session per application request.

    The session is always closed after the request completes,
    whether the request succeeds or raises an exception.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
