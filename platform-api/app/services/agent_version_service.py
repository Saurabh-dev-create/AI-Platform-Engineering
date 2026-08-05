from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import AgentVersionStatus ,TeamRole
from app.core.exceptions import (
    PlatformException,
    ResourceConflictException,
    ResourceNotFoundException,
)
from app.models.agent import Agent
from app.models.agent_version import AgentVersion
from app.models.user import User
from app.repositories.agent_repository import AgentRepository
from app.repositories.agent_version_repository import (
    AgentVersionRepository,
)
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.schemas.agent_version import AgentVersionCreate


class AgentVersionService:
    """
    Business logic for project-scoped AI agent version lifecycle.
    """

    def __init__(
        self,
        version_repository: AgentVersionRepository,
        agent_repository: AgentRepository,
        project_repository: ProjectRepository,
        membership_repository: TeamMembershipRepository,
    ) -> None:
        self.version_repository = version_repository
        self.agent_repository = agent_repository
        self.project_repository = project_repository
        self.membership_repository = membership_repository

    def _require_agent_access(
        self,
        db: Session,
        *,
        agent_id: UUID,
        current_user: User,
    ) -> tuple[Agent, TeamRole]:
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

        project = self.project_repository.get_for_user_by_id(
            db,
            project_id=agent.project_id,
            user_id=current_user.id,
        )

        if project is None:
            raise ResourceNotFoundException(
                resource="Agent",
                resource_id=str(agent_id),
            )

        membership = self.membership_repository.get_by_user_and_team(
            db,
            user_id=current_user.id,
            team_id=project.team_id,
        )

        if membership is None:
            raise ResourceNotFoundException(
                resource="Agent",
                resource_id=str(agent_id),
            )

        return agent, membership.role

    def _require_version_creator(
        self,
        db: Session,
        *,
        agent_id: UUID,
        current_user: User,
    ) -> Agent:
        agent, role = self._require_agent_access(
            db,
            agent_id=agent_id,
            current_user=current_user,
        )

        if role not in {
            TeamRole.TEAM_ADMIN,
            TeamRole.DEVELOPER,
        }:
            raise PlatformException(
                message=(
                    "Agent version creation requires "
                    "team_admin or developer role"
                ),
                error_code="AGENT_VERSION_CREATE_FORBIDDEN",
                status_code=403,
            )

        return agent

    def create_version(
        self,
        db: Session,
        *,
        agent_id: UUID,
        current_user: User,
        version_data: AgentVersionCreate,
    ) -> AgentVersion:
        self._require_version_creator(
            db,
            agent_id=agent_id,
            current_user=current_user,
        )

        latest_version = self.version_repository.get_latest_for_agent(
            db,
            agent_id=agent_id,
        )

        next_version_number = (
            1
            if latest_version is None
            else latest_version.version_number + 1
        )

        normalized_prompt = (
            version_data.prompt_template.strip()
            if version_data.prompt_template is not None
            else None
        )

        normalized_summary = (
            version_data.change_summary.strip()
            if version_data.change_summary is not None
            else None
        )

        try:
            version = self.version_repository.create(
                db,
                agent_id=agent_id,
                version_number=next_version_number,
                model_config=version_data.model_config_data,
                prompt_template=normalized_prompt,
                runtime_config=version_data.runtime_config,
                tool_config=version_data.tool_config,
                change_summary=normalized_summary,
                created_by_user_id=current_user.id,
            )

            db.commit()
            db.refresh(version)

            return version

        except IntegrityError as exc:
            db.rollback()

            raise ResourceConflictException(
                resource="AgentVersion",
                field="version_number",
                value=str(next_version_number),
            ) from exc

    def list_versions(
        self,
        db: Session,
        *,
        agent_id: UUID,
        current_user: User,
    ) -> list[AgentVersion]:
        self._require_agent_access(
            db,
            agent_id=agent_id,
            current_user=current_user,
        )

        return self.version_repository.list_for_agent(
            db,
            agent_id=agent_id,
        )

    def get_version(
        self,
        db: Session,
        *,
        version_id: UUID,
        current_user: User,
    ) -> AgentVersion:
        version = self.version_repository.get_for_user_by_id(
            db,
            version_id=version_id,
            user_id=current_user.id,
        )

        if version is None:
            raise ResourceNotFoundException(
                resource="AgentVersion",
                resource_id=str(version_id),
            )

        return version
    def publish_version(
        self,
        db: Session,
        *,
        version_id: UUID,
        current_user: User,
    ) -> AgentVersion:
        version = self.version_repository.get_for_user_by_id(
            db,
            version_id=version_id,
            user_id=current_user.id,
        )

        if version is None:
            raise ResourceNotFoundException(
                resource="AgentVersion",
                resource_id=str(version_id),
            )

        _, role = self._require_agent_access(
            db,
            agent_id=version.agent_id,
            current_user=current_user,
        )

        if role not in {
            TeamRole.TEAM_ADMIN,
            TeamRole.DEVELOPER,
        }:
            raise PlatformException(
                message=(
                    "Publishing an agent version requires "
                    "team_admin or developer role"
                ),
                error_code="AGENT_VERSION_PUBLISH_FORBIDDEN",
                status_code=403,
            )

        if version.status != AgentVersionStatus.DRAFT:
            raise PlatformException(
                message=(
                    "Only draft agent versions can be published"
                ),
                error_code="INVALID_AGENT_VERSION_TRANSITION",
                status_code=409,
            )

        version = self.version_repository.update_status(
            db,
            version=version,
            status=AgentVersionStatus.PUBLISHED,
        )

        db.commit()
        db.refresh(version)

        return version

    def deprecate_version(
        self,
        db: Session,
        *,
        version_id: UUID,
        current_user: User,
    ) -> AgentVersion:
        version = self.version_repository.get_for_user_by_id(
            db,
            version_id=version_id,
            user_id=current_user.id,
        )

        if version is None:
            raise ResourceNotFoundException(
                resource="AgentVersion",
                resource_id=str(version_id),
            )

        _, role = self._require_agent_access(
            db,
            agent_id=version.agent_id,
            current_user=current_user,
        )

        if role not in {
            TeamRole.TEAM_ADMIN,
            TeamRole.DEVELOPER,
        }:
            raise PlatformException(
                message=(
                    "Deprecating an agent version requires "
                    "team_admin or developer role"
                ),
                error_code="AGENT_VERSION_DEPRECATE_FORBIDDEN",
                status_code=403,
            )

        if version.status != AgentVersionStatus.PUBLISHED:
            raise PlatformException(
                message=(
                    "Only published agent versions can be deprecated"
                ),
                error_code="INVALID_AGENT_VERSION_TRANSITION",
                status_code=409,
            )

        version = self.version_repository.update_status(
            db,
            version=version,
            status=AgentVersionStatus.DEPRECATED,
        )

        db.commit()
        db.refresh(version)

        return version
