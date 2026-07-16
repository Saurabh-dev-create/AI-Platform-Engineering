from uuid import UUID

from sqlalchemy import func , select
from sqlalchemy.orm import Session

from app.core.constants import TeamRole
from app.models.team_membership import TeamMembership


class TeamMembershipRepository:
    """
    Database access layer for team memberships.

    Memberships connect users to teams and assign team-scoped roles.
    """

    def get_by_user_and_team(
        self,
        db: Session,
        *,
        user_id: UUID,
        team_id: UUID,
    ) -> TeamMembership | None:
        statement = select(TeamMembership).where(
            TeamMembership.user_id == user_id,
            TeamMembership.team_id == team_id,
        )

        return db.scalar(statement)

    def create(
        self,
        db: Session,
        *,
        user_id: UUID,
        team_id: UUID,
        role: TeamRole,
    ) -> TeamMembership:
        membership = TeamMembership(
            user_id=user_id,
            team_id=team_id,
            role=role,
        )

        db.add(membership)
        db.flush()
        db.refresh(membership)

        return membership

    def list_for_team(
        self,
        db: Session,
        *,
        team_id: UUID,
    ) -> list[TeamMembership]:
        statement = (
            select(TeamMembership)
            .where(
                TeamMembership.team_id == team_id,
            )
            .order_by(TeamMembership.created_at)
        )

        return list(
            db.scalars(statement).all()
        )

    def update_role(
        self,
        db: Session,
        *,
        membership: TeamMembership,
        role: TeamRole,
    ) -> TeamMembership:
        membership.role = role

        db.flush()
        db.refresh(membership)

        return membership

    def delete(
        self,
        db: Session,
        *,
        membership: TeamMembership,
    ) -> None:
        db.delete(membership)
        db.flush()
    def count_for_team_by_role(
        self,
        db: Session,
        *,
        team_id: UUID,
        role: TeamRole,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(TeamMembership)
            .where(
                TeamMembership.team_id == team_id,
                TeamMembership.role == role,
            )
        )

        return int(
            db.scalar(statement) or 0
            )
