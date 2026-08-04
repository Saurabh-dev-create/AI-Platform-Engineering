from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import AgentStatus
from app.models.agent import Agent
from app.models.project import Project
from app.models.team_membership import TeamMembership


class AgentRepository:
    """
    Database access layer for project-owned AI agents.
    """

    def get_for_user_by_id(
        self,
        db: Session,
        *,
        agent_id: UUID,
        user_id: UUID,
    ) -> Agent | None:
        """
        Return an agent only when the requesting user belongs to the team
        that owns the agent's project.
        """

        statement = (
            select(Agent)
            .join(
                Project,
                Project.id == Agent.project_id,
            )
            .join(
                TeamMembership,
                TeamMembership.team_id == Project.team_id,
            )
            .where(
                Agent.id == agent_id,
                TeamMembership.user_id == user_id,
            )
        )

        return db.scalar(statement)

    def get_by_project_and_slug(
        self,
        db: Session,
        *,
        project_id: UUID,
        slug: str,
    ) -> Agent | None:
        statement = (
            select(Agent)
            .where(
                Agent.project_id == project_id,
                Agent.slug == slug,
            )
        )

        return db.scalar(statement)

    def list_for_project(
        self,
        db: Session,
        *,
        project_id: UUID,
    ) -> list[Agent]:
        statement = (
            select(Agent)
            .where(
                Agent.project_id == project_id,
            )
            .order_by(Agent.created_at)
        )

        return list(
            db.scalars(statement).all()
        )

    def create(
        self,
        db: Session,
        *,
        project_id: UUID,
        name: str,
        slug: str,
        description: str | None,
    ) -> Agent:
        agent = Agent(
            project_id=project_id,
            name=name,
            slug=slug,
            description=description,
            status=AgentStatus.DRAFT,
        )

        db.add(agent)
        db.flush()
        db.refresh(agent)

        return agent

    def update(
        self,
        db: Session,
        *,
        agent: Agent,
        name: str | None = None,
        description: str | None = None,
        status: AgentStatus | None = None,
    ) -> Agent:
        if name is not None:
            agent.name = name

        if description is not None:
            agent.description = description

        if status is not None:
            agent.status = status

        db.flush()
        db.refresh(agent)

        return agent
