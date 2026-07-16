from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.constants import TeamRole


class TeamMemberAdd(BaseModel):
    email: EmailStr
    role: TeamRole = TeamRole.DEVELOPER


class TeamMemberRoleUpdate(BaseModel):
    role: TeamRole


class TeamMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    team_id: UUID
    role: TeamRole
    created_at: datetime
    updated_at: datetime
