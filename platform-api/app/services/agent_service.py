from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import TeamRole
from app.core.exceptions import (
    PlatformException,
    ResourceConflictException,
    ResourceNotFoundException,
)
from app.models.agent import Agent
from app.models.user import User
from app.repositories.agent_repository import AgentRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.schemas.agent import AgentCreate


class AgentService:
    """
    Business logic for project-scoped AI agent registration and access.
    """

    def __init__(
        self,
        agent_repository: AgentRepository,
        project_repository: ProjectRepository,
        membership_repository: TeamMembershipRepository,
    ) -> None:
        self.agent_repository = agent_repository
        self.project_repository = project_repository
        self.membership_repository = membership_repository

    def _require_project_access(
        self,
        db: Session,
        *,
        project_id: UUID,
        current_user: User,
    ) -> tuple:
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

        membership = self.membership_repository.get_by_user_and_team(
            db,
            user_id=current_user.id,
            team_id=project.team_id,
        )

        if membership is None:
            raise ResourceNotFoundException(
                resource="Project",
                resource_id=str(project_id),
            )

        return project, membership.role

    def _require_agent_creator(
        self,
        db: Session,
        *,
        project_id: UUID,
        current_user: User,
    ) -> None:
        _, role = self._require_project_access(
            db,
            project_id=project_id,
            current_user=current_user,
        )

        if role not in {
            TeamRole.TEAM_ADMIN,
            TeamRole.DEVELOPER,
        }:
            raise PlatformException(
                message="Agent creation requires team_admin or developer role",
                error_code="AGENT_CREATE_FORBIDDEN",
                status_code=403,
            )

    def create_agent(
        self,
        db: Session,
        *,
        project_id: UUID,
        current_user: User,
        agent_data: AgentCreate,
    ) -> Agent:
        self._require_agent_creator(
            db,
            project_id=project_id,
            current_user=current_user,
        )

        normalized_name = agent_data.name.strip()
        normalized_slug = agent_data.slug.lower()
        normalized_description = (
            agent_data.description.strip()
            if agent_data.description is not None
            else None
        )

        existing_agent = self.agent_repository.get_by_project_and_slug(
            db,
            project_id=project_id,
            slug=normalized_slug,
        )

        if existing_agent is not None:
            raise ResourceConflictException(
                resource="Agent",
                field="slug",
                value=normalized_slug,
            )

        try:
            agent = self.agent_repository.create(
                db,
                project_id=project_id,
                name=normalized_name,
                slug=normalized_slug,
                description=normalized_description,
            )

            db.commit()
            db.refresh(agent)

            return agent

        except IntegrityError as exc:
            db.rollback()

            raise ResourceConflictException(
                resource="Agent",
                field="slug",
                value=normalized_slug,
            ) from exc

    def list_agents(
        self,
        db: Session,
        *,
        project_id: UUID,
        current_user: User,
    ) -> list[Agent]:
        self._require_project_access(
            db,
            project_id=project_id,
            current_user=current_user,
        )

        return self.agent_repository.list_for_project(
            db,
            project_id=project_id,
        )

    def get_agent(
        self,
        db: Session,
        *,
        agent_id: UUID,
        current_user: User,
    ) -> Agent:
        agent = self.agent_repository.get_for_user_by_id(
            db,
            agent_id=agent_id,
            user_id=current_user.id,
        )

        if agent is None:
            raise ResourceNotFoundException(
                resource="Agent",
                resource_id=str(agent_id),
            )

        return agent
