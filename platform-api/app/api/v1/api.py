from fastapi import APIRouter

from app.api.v1 import (
    agent_versions,
    agents,
    auth,
    deployments,
    health,
    projects,
    teams,
)


api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(health.router)
api_v1_router.include_router(teams.router)
api_v1_router.include_router(projects.router)
api_v1_router.include_router(agents.router)
api_v1_router.include_router(agent_versions.router)
api_v1_router.include_router(deployments.router)
