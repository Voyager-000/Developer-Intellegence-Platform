from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.engines.deployment_engine import DeploymentValidationEngine
from backend.app.models.entities import DeploymentValidation, DeploymentCheck, generate_id
from backend.app.schemas.schemas import DeploymentValidationRequest, DeploymentValidationResponse, DeploymentCheckSchema, ResponseEnvelope

router = APIRouter(prefix="/deployment", tags=["Deployment Validation"])

@router.post("/validations", response_model=ResponseEnvelope[DeploymentValidationResponse])
def run_deployment_validation(req: DeploymentValidationRequest, db: Session = Depends(get_db)):
    result = DeploymentValidationEngine.validate_deployment()

    dep_id = generate_id("dep")
    dep = DeploymentValidation(
        id=dep_id,
        project_id=req.project_id,
        readiness_score=result["readiness_score"],
        decision=result["decision"],
        warnings_count=result["warnings_count"],
        blockers_count=result["blockers_count"],
        code_quality_score=result["code_quality_score"],
        security_score=result["security_score"],
        testing_score=result["testing_score"],
        dependencies_score=result["dependencies_score"],
        configuration_score=result["configuration_score"],
        performance_score=result["performance_score"]
    )
    db.add(dep)

    check_schemas = []
    for c in result["checks"]:
        depc = DeploymentCheck(
            id=generate_id("depc"),
            validation_id=dep_id,
            pillar=c["pillar"],
            status=c["status"],
            details=c["details"]
        )
        db.add(depc)
        check_schemas.append(DeploymentCheckSchema(
            pillar=c["pillar"],
            status=c["status"],
            details=c["details"]
        ))

    db.commit()

    # Sync to Turso cloud
    try:
        from backend.app.core.turso import turso_client
        if turso_client.is_configured():
            turso_client.sync_deployment_validation(
                dep.id, dep.project_id or "default", dep.readiness_score,
                dep.decision, dep.warnings_count, dep.blockers_count
            )
    except Exception:
        pass

    return ResponseEnvelope(
        data=DeploymentValidationResponse(
            validation_id=dep_id,
            readiness_score=result["readiness_score"],
            decision=result["decision"],
            warnings_count=result["warnings_count"],
            blockers_count=result["blockers_count"],
            code_quality_score=result["code_quality_score"],
            security_score=result["security_score"],
            testing_score=result["testing_score"],
            dependencies_score=result["dependencies_score"],
            configuration_score=result["configuration_score"],
            performance_score=result["performance_score"],
            checks=check_schemas
        ),
        request_id=generate_id("req")
    )

@router.get("/validations/{val_id}", response_model=ResponseEnvelope[DeploymentValidationResponse])
def get_deployment_validation(val_id: str, db: Session = Depends(get_db)):
    dep = db.query(DeploymentValidation).filter(DeploymentValidation.id == val_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment validation not found")

    checks = [
        DeploymentCheckSchema(
            pillar=c.pillar,
            status=c.status,
            details=c.details
        ) for c in dep.checks
    ]

    return ResponseEnvelope(
        data=DeploymentValidationResponse(
            validation_id=dep.id,
            readiness_score=dep.readiness_score,
            decision=dep.decision,
            warnings_count=dep.warnings_count,
            blockers_count=dep.blockers_count,
            code_quality_score=dep.code_quality_score,
            security_score=dep.security_score,
            testing_score=dep.testing_score,
            dependencies_score=dep.dependencies_score,
            configuration_score=dep.configuration_score,
            performance_score=dep.performance_score,
            checks=checks
        ),
        request_id=generate_id("req")
    )

@router.get("/reports/{project_id}", response_model=ResponseEnvelope[dict])
def get_deployment_report(project_id: str, db: Session = Depends(get_db)):
    latest = db.query(DeploymentValidation).filter(DeploymentValidation.project_id == project_id).order_by(DeploymentValidation.created_at.desc()).first()
    if not latest:
        val = DeploymentValidationEngine.validate_deployment()
        return ResponseEnvelope(data=val, request_id=generate_id("req"))

    return ResponseEnvelope(
        data={
            "project_id": project_id,
            "validation_id": latest.id,
            "overall_score": latest.readiness_score,
            "decision": latest.decision,
            "blockers_count": latest.blockers_count,
            "warnings_count": latest.warnings_count,
            "pillars": {
                "code_quality": latest.code_quality_score,
                "security": latest.security_score,
                "testing": latest.testing_score,
                "dependencies": latest.dependencies_score,
                "configuration": latest.configuration_score,
                "performance": latest.performance_score
            }
        },
        request_id=generate_id("req")
    )
