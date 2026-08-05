from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.constants import AgentVersionStatus
from app.models.agent import Agent
from app.models.agent_version import AgentVersion
from app.models.project import Project
from app.models.team_membership import TeamMembership


class AgentVersionRepository:
    """
    Database access layer for versioned AI agent configurations.
    """

    def get_for_user_by_id(
        self,
        db: Session,
        *,
        version_id: UUID,
        user_id: UUID,
    ) -> AgentVersion | None:
        statement = (
            select(AgentVersion)
            .join(
                Agent,
                Agent.id == AgentVersion.agent_id,
            )
            .join(
                Project,
                Project.id == Agent.project_id,
            )
            .join(
                TeamMembership,
                TeamMembership.team_id == Project.team_id,
            )
            .where(
                AgentVersion.id == version_id,
                TeamMembership.user_id == user_id,
            )
        )

        return db.scalar(statement)

    def list_for_agent(
        self,
        db: Session,
        *,
        agent_id: UUID,
    ) -> list[AgentVersion]:
        statement = (
            select(AgentVersion)
            .where(
                AgentVersion.agent_id == agent_id,
            )
            .order_by(AgentVersion.version_number)
        )

        return list(
            db.scalars(statement).all()
        )

    def get_latest_for_agent(
        self,
        db: Session,
        *,
        agent_id: UUID,
    ) -> AgentVersion | None:
        statement = (
            select(AgentVersion)
            .where(
                AgentVersion.agent_id == agent_id,
            )
            .order_by(
                desc(AgentVersion.version_number),
            )
            .limit(1)
        )

        return db.scalar(statement)

    def create(
        self,
        db: Session,
        *,
        agent_id: UUID,
        version_number: int,
        model_config: dict,
        prompt_template: str | None,
        runtime_config: dict,
        tool_config: dict,
        change_summary: str | None,
        created_by_user_id: UUID,
    ) -> AgentVersion:
        version = AgentVersion(
            agent_id=agent_id,
            version_number=version_number,
            status=AgentVersionStatus.DRAFT,
            model_config=model_config,
            prompt_template=prompt_template,
            runtime_config=runtime_config,
            tool_config=tool_config,
            change_summary=change_summary,
            created_by_user_id=created_by_user_id,
        )

        db.add(version)
        db.flush()
        db.refresh(version)

        return version
    def update_status(
        self,
        db: Session,
        *,
        version: AgentVersion,
        status: AgentVersionStatus,
    ) -> AgentVersion:
        """
        Persist an AgentVersion lifecycle status change.

        Lifecycle transition validation belongs to the service layer.
        """

        version.status = status

        db.flush()
        db.refresh(version)

        return version
