from enum import StrEnum


class TeamRole(StrEnum):
    TEAM_ADMIN = "team_admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class AgentStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
