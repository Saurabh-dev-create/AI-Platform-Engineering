from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class AgentStatus(StrEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    DEPLOYING = "deploying"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPED = "stopped"


class DeploymentStatus(StrEnum):
    PENDING = "pending"
    APPROVAL_REQUIRED = "approval_required"
    APPROVED = "approved"
    GENERATING = "generating"
    GIT_COMMITTED = "git_committed"
    SYNCING = "syncing"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentEnvironment(StrEnum):
    DEVELOPMENT = "dev"
    STAGING = "stage"
    PRODUCTION = "prod"


class UserRole(StrEnum):
    PLATFORM_ADMIN = "platform_admin"
    TEAM_ADMIN = "team_admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class AuditAction(StrEnum):
    USER_LOGIN = "user_login"
    AGENT_CREATED = "agent_created"
    AGENT_UPDATED = "agent_updated"
    AGENT_DELETED = "agent_deleted"
    DEPLOYMENT_REQUESTED = "deployment_requested"
    DEPLOYMENT_APPROVED = "deployment_approved"
    DEPLOYMENT_REJECTED = "deployment_rejected"
    DEPLOYMENT_ROLLED_BACK = "deployment_rolled_back"
    POLICY_VIOLATION = "policy_violation"
    BUDGET_LIMIT_REACHED = "budget_limit_reached"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"


class AIProvider(StrEnum):
    OPENAI = "openai"
    BEDROCK = "bedrock"
    OLLAMA = "ollama"
    VLLM = "vllm"


class LogEvent(StrEnum):
    APPLICATION_STARTED = "application_started"
    APPLICATION_STOPPED = "application_stopped"
    REQUEST_STARTED = "request_started"
    REQUEST_COMPLETED = "request_completed"
    REQUEST_FAILED = "request_failed"
    DATABASE_CONNECTED = "database_connected"
    DATABASE_CONNECTION_FAILED = "database_connection_failed"
    REDIS_CONNECTED = "redis_connected"
    REDIS_CONNECTION_FAILED = "redis_connection_failed"
    AGENT_DEPLOYMENT_REQUESTED = "agent_deployment_requested"
    AI_REQUEST_COMPLETED = "ai_request_completed"
    AI_REQUEST_FAILED = "ai_request_failed"
