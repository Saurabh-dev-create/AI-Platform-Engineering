from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.team_membership import TeamMembership


class TeamRepository:
    """
    Database access layer for platform teams.

    Team queries are scoped through memberships when retrieving teams
    visible to a particular platform user.
    """

    def get_by_id(
        self,
        db: Session,
        team_id: UUID,
    ) -> Team | None:
        statement = select(Team).where(
            Team.id == team_id,
        )

        return db.scalar(statement)

    def get_by_slug(
        self,
        db: Session,
        slug: str,
    ) -> Team | None:
        statement = select(Team).where(
            Team.slug == slug,
        )

        return db.scalar(statement)

    def list_for_user(
        self,
        db: Session,
        user_id: UUID,
    ) -> list[Team]:
        statement = (
            select(Team)
            .join(
                TeamMembership,
                TeamMembership.team_id == Team.id,
            )
            .where(
                TeamMembership.user_id == user_id,
                Team.is_active.is_(True),
            )
            .order_by(Team.name)
        )

        return list(
            db.scalars(statement).all()
        )

    def create(
        self,
        db: Session,
        *,
        name: str,
        slug: str,
        description: str | None,
    ) -> Team:
        team = Team(
            name=name,
            slug=slug,
            description=description,
        )

        db.add(team)
        db.flush()
        db.refresh(team)

        return team
    def get_for_user_by_id(
        self,
        db: Session,
        *,
        team_id: UUID,
        user_id: UUID,
    ) -> Team | None:
        statement = (
            select(Team)
            .join(
                TeamMembership,
                TeamMembership.team_id == Team.id,
            )
            .where(
                Team.id == team_id,
                TeamMembership.user_id == user_id,
                Team.is_active.is_(True),
            )
        )

        return db.scalar(statement)
