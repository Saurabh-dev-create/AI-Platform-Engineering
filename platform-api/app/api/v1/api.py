from fastapi import APIRouter

from app.api.v1 import auth, health, teams , projects , teams


api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(health.router)
api_v1_router.include_router(teams.router)
api_v1_router.include_router(projects.router)
