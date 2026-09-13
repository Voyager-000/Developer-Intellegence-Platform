from fastapi import APIRouter
from backend.app.schemas.schemas import ResponseEnvelope
from backend.app.core.config import settings
from backend.app.core.turso import turso_client

router = APIRouter(tags=["System & Health"])

@router.get("/health", response_model=ResponseEnvelope[dict])
def health_check():
    turso_info = turso_client.get_cloud_status() if turso_client.is_configured() else {"status": "disabled"}
    return ResponseEnvelope(
        data={
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "cloud_database": turso_info
        },
        request_id="req_health"
    )

@router.get("/turso/status", response_model=ResponseEnvelope[dict])
def get_turso_status():
    cloud_status = turso_client.get_cloud_status()
    return ResponseEnvelope(data=cloud_status, request_id="req_turso")

@router.get("/system/status", response_model=ResponseEnvelope[dict])
def system_status():
    return ResponseEnvelope(
        data={
            "status": "operational",
            "engines": {
                "smart_repo_context_engine": "active",
                "code_intelligence_engine": "active",
                "self_correction_engine": "active",
                "fix_validation_engine": "active",
                "database_optimization_engine": "active",
                "security_analysis_engine": "active",
                "deployment_validation_engine": "active"
            },
            "cloud_db": {
                "configured": turso_client.is_configured(),
                "provider": "Turso (libSQL)",
                "region": "aws-ap-south-1"
            },
            "features": {
                "ai_fixes": settings.ENABLE_AI_FIXES,
                "db_optimizer": settings.ENABLE_DB_OPTIMIZER,
                "security_scan": settings.ENABLE_SECURITY_SCAN,
                "deployment_validation": settings.ENABLE_DEPLOYMENT_VALIDATION
            }
        },
        request_id="req_status"
    )

