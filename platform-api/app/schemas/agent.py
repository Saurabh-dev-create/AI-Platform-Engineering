from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import AgentStatus


class AgentCreate(BaseModel):
    """
    Request schema for registering a new AI agent under a project.

    Agent identity is created here. Version-specific configuration such as
    model, prompt, runtime settings, temperature, token limits, and provider
    configuration will belong to AgentVersion.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    slug: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class AgentUpdate(BaseModel):
    """
    Request schema for updating mutable agent metadata and lifecycle status.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    status: AgentStatus | None = None


class AgentResponse(BaseModel):
    """
    Response schema returned for registered AI agents.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    slug: str
    description: str | None
    status: AgentStatus
    created_at: datetime
    updated_at: datetime
