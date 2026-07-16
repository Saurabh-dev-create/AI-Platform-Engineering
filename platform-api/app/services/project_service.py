from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import TeamRole
from app.core.exceptions import (
    PlatformException,
    ResourceConflictException,
    ResourceNotFoundException,
)
from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.repositories.team_repository import TeamRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    """
    Business logic for tenant-scoped project lifecycle.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        team_repository: TeamRepository,
        membership_repository: TeamMembershipRepository,
    ) -> None:
        self.project_repository = project_repository
        self.team_repository = team_repository
        self.membership_repository = membership_repository

    def _require_team_member(
        self,
        db: Session,
        *,
        team_id: UUID,
        current_user: User,
    ) -> TeamRole:
        team = self.team_repository.get_for_user_by_id(
            db,
            team_id=team_id,
            user_id=current_user.id,
        )

        if team is None:
            raise ResourceNotFoundException(
                resource="Team",
                resource_id=str(team_id),
            )

        membership = self.membership_repository.get_by_user_and_team(
            db,
            user_id=current_user.id,
            team_id=team_id,
        )

        if membership is None:
            raise ResourceNotFoundException(
                resource="Team",
                resource_id=str(team_id),
            )

        return membership.role

    def _require_project_creator(
        self,
        db: Session,
        *,
        team_id: UUID,
        current_user: User,
    ) -> None:
        role = self._require_team_member(
            db,
            team_id=team_id,
            current_user=current_user,
        )

        if role not in {
            TeamRole.TEAM_ADMIN,
            TeamRole.DEVELOPER,
        }:
            raise PlatformException(
                message="Project creation requires team_admin or developer role",
                error_code="PROJECT_CREATE_FORBIDDEN",
                status_code=403,
            )

    def create_project(
        self,
        db: Session,
        *,
        team_id: UUID,
        current_user: User,
        project_data: ProjectCreate,
    ) -> Project:
        self._require_project_creator(
            db,
            team_id=team_id,
            current_user=current_user,
        )

        normalized_name = project_data.name.strip()
        normalized_slug = project_data.slug.lower()
        normalized_description = (
            project_data.description.strip()
            if project_data.description is not None
            else None
        )

        existing_project = self.project_repository.get_by_team_and_slug(
            db,
            team_id=team_id,
            slug=normalized_slug,
        )

        if existing_project is not None:
            raise ResourceConflictException(
                resource="Project",
                field="slug",
                value=normalized_slug,
            )

        try:
            project = self.project_repository.create(
                db,
                team_id=team_id,
                name=normalized_name,
                slug=normalized_slug,
                description=normalized_description,
            )

            db.commit()
            db.refresh(project)

            return project

        except IntegrityError as exc:
            db.rollback()

            raise ResourceConflictException(
                resource="Project",
                field="slug",
                value=normalized_slug,
            ) from exc

    def list_projects(
        self,
        db: Session,
        *,
        team_id: UUID,
        current_user: User,
    ) -> list[Project]:
        self._require_team_member(
            db,
            team_id=team_id,
            current_user=current_user,
        )

        return self.project_repository.list_for_team(
            db,
            team_id=team_id,
        )

    def get_project(
        self,
        db: Session,
        *,
        project_id: UUID,
        current_user: User,
    ) -> Project:
        project = self.project_repository.get_for_user_by_id(
            db,
            project_id=project_id,
            user_id=current_user.id,
        )

        if project is None:
            raise ResourceNotFoundException(
                resource="Project",
                resource_id=str(project_id),
            )

        return project
