from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.team_membership import TeamMembership


class ProjectRepository:
    """
    Database access layer for team-owned projects.
    """

    def get_for_user_by_id(
        self,
        db: Session,
        *,
        project_id: UUID,
        user_id: UUID,
    ) -> Project | None:
        statement = (
            select(Project)
            .join(
                TeamMembership,
                TeamMembership.team_id == Project.team_id,
            )
            .where(
                Project.id == project_id,
                TeamMembership.user_id == user_id,
            )
        )

        return db.scalar(statement)

    def get_by_team_and_slug(
        self,
        db: Session,
        *,
        team_id: UUID,
        slug: str,
    ) -> Project | None:
        statement = (
            select(Project)
            .where(
                Project.team_id == team_id,
                Project.slug == slug,
            )
        )

        return db.scalar(statement)

    def list_for_team(
        self,
        db: Session,
        *,
        team_id: UUID,
    ) -> list[Project]:
        statement = (
            select(Project)
            .where(
                Project.team_id == team_id,
            )
            .order_by(Project.created_at)
        )

        return list(
            db.scalars(statement).all()
        )


    def count_for_team(
        self,
        db: Session,
        *,
        team_id: UUID,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(Project)
            .where(
                Project.team_id == team_id,
            )
        )

        return int(
            db.scalar(statement) or 0
        )

    def create(
        self,
        db: Session,
        *,
        team_id: UUID,
        name: str,
        slug: str,
        description: str | None,
    ) -> Project:
        project = Project(
            team_id=team_id,
            name=name,
            slug=slug,
            description=description,
        )

        db.add(project)
        db.flush()
        db.refresh(project)

        return project
