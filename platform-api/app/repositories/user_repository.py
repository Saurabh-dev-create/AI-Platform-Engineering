from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Database access layer for platform users.

    The repository isolates SQLAlchemy query details from the service layer.
    """

    def get_by_id(
        self,
        db: Session,
        user_id: UUID,
    ) -> User | None:
        statement = select(User).where(User.id == user_id)

        return db.scalar(statement)

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> User | None:
        statement = select(User).where(User.email == email)

        return db.scalar(statement)

    def create(
        self,
        db: Session,
        *,
        email: str,
        password_hash: str,
        full_name: str,
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
        )

        db.add(user)
        db.flush()
        db.refresh(user)

        return user
