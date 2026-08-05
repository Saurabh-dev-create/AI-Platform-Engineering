from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import AgentVersionStatus


class AgentVersionCreate(BaseModel):
    """
    Request schema for creating a new draft version of an AI agent.

    Version numbers and lifecycle status are controlled by the platform.
    Clients provide the configuration snapshot for the new version.
    """

    model_config_data: dict[str, Any] = Field(
        default_factory=dict,
        alias="model_config",
    )

    prompt_template: str | None = None

    runtime_config: dict[str, Any] = Field(
        default_factory=dict,
    )

    tool_config: dict[str, Any] = Field(
        default_factory=dict,
    )

    change_summary: str | None = Field(
        default=None,
        max_length=1000,
    )


class AgentVersionResponse(BaseModel):
    """
    Response schema for a versioned AI agent configuration snapshot.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    agent_id: UUID
    version_number: int
    status: AgentVersionStatus

    model_config_data: dict[str, Any] = Field(
        alias="model_config",
    )

    prompt_template: str | None
    runtime_config: dict[str, Any]
    tool_config: dict[str, Any]

    change_summary: str | None
    created_by_user_id: UUID | None

    created_at: datetime
    updated_at: datetime
