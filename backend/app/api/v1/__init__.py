from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.projects import router as projects_router
from backend.app.api.v1.analysis import router as analysis_router
from backend.app.api.v1.database import router as database_router
from backend.app.api.v1.security import router as security_router
from backend.app.api.v1.deployment import router as deployment_router
from backend.app.api.v1.feedback import router as feedback_router
from backend.app.api.v1.health import router as health_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(projects_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(database_router)
api_v1_router.include_router(security_router)
api_v1_router.include_router(deployment_router)
api_v1_router.include_router(feedback_router)

__all__ = ["api_v1_router"]
