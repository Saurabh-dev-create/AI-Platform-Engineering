from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.connection import engine


def get_db_session() -> Generator[Session, None, None]:
    """
    Provide a SQLAlchemy session for one Platform API request.

    The session is always closed after the request finishes,
    including when the request raises an exception.
    """

    with Session(engine) as db:
        yield db
