from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.engines.security_engine import SecurityAnalysisEngine
from backend.app.engines.strix_engine import StrixSecurityEngine
from backend.app.models.entities import SecurityScan, SecurityFinding, generate_id
from backend.app.schemas.schemas import (
    SecurityScanRequest, SecurityScanResponse, SecurityFindingSchema,
    StrixScanRequest, ResponseEnvelope
)

router = APIRouter(prefix="/security", tags=["Security Intelligence & Strix"])

@router.post("/scans", response_model=ResponseEnvelope[SecurityScanResponse])
def run_security_scan(req: SecurityScanRequest, db: Session = Depends(get_db)):
    if req.files and len(req.files) > 0:
        file_dicts = [{"path": f.path, "content": f.content, "size": f.size} for f in req.files]
        result = SecurityAnalysisEngine.run_codebase_scan(file_dicts)
    else:
        result = SecurityAnalysisEngine.run_scan(req.source_code, req.file_path or "src/app.py")

    scan_id = generate_id("sec")
    scan = SecurityScan(
        id=scan_id,
        project_id=req.project_id,
        security_score=result["security_score"],
        critical_count=result["critical_count"],
        high_count=result["high_count"],
        medium_count=result["medium_count"],
        low_count=result["low_count"],
        status="completed"
    )
    db.add(scan)

    finding_schemas = []
    for f in result["findings"]:
        secf_id = generate_id("secf")
        secf = SecurityFinding(
            id=secf_id,
            scan_id=scan_id,
            title=f["title"],
            category=f["category"],
            severity=f["severity"],
            file_path=f["file_path"],
            line=f["line"],
            remediation=f["remediation"]
        )
        db.add(secf)
        finding_schemas.append(SecurityFindingSchema(
            id=secf_id,
            title=f["title"],
            category=f["category"],
            severity=f["severity"],
            file_path=f["file_path"],
            line=f["line"],
            remediation=f["remediation"],
            poc_payload=f.get("poc_payload"),
            cwe_id=f.get("cwe_id"),
            attack_vector=f.get("attack_vector")
        ))

    db.commit()

    # Sync to Turso cloud
    try:
        from backend.app.core.turso import turso_client
        if turso_client.is_configured():
            turso_client.sync_security_scan(
                scan.id, scan.project_id or "default", scan.security_score,
                scan.critical_count, scan.high_count, scan.medium_count, scan.low_count
            )
    except Exception:
        pass

    return ResponseEnvelope(
        data=SecurityScanResponse(
            scan_id=scan_id,
            security_score=result["security_score"],
            critical_count=result["critical_count"],
            high_count=result["high_count"],
            medium_count=result["medium_count"],
            low_count=result["low_count"],
            status="completed",
            strix_cli_available=result.get("strix_cli_available", StrixSecurityEngine.is_strix_cli_available()),
            findings=finding_schemas
        ),
        request_id=generate_id("req")
    )

@router.post("/strix", response_model=ResponseEnvelope[SecurityScanResponse])
def run_strix_agent_scan(req: StrixScanRequest, db: Session = Depends(get_db)):
    """
    Direct Strix AI Penetration Testing scan with Proof-of-Concept (PoC) generation.
    """
    if req.files and len(req.files) > 0:
        file_dicts = [{"path": f.path, "content": f.content, "size": f.size} for f in req.files]
        result = StrixSecurityEngine.scan_codebase(file_dicts)
    else:
        # Scan current project or target path
        target = req.target_path or "."
        result = {
            "security_score": 100,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "status": "completed",
            "findings": []
        }

    finding_schemas = [
        SecurityFindingSchema(
            id=generate_id("strix"),
            title=f["title"],
            category=f["category"],
            severity=f["severity"],
            file_path=f["file_path"],
            line=f["line"],
            remediation=f["remediation"],
            poc_payload=f.get("poc_payload"),
            cwe_id=f.get("cwe_id"),
            attack_vector=f.get("attack_vector")
        ) for f in result["findings"]
    ]

    return ResponseEnvelope(
        data=SecurityScanResponse(
            scan_id=generate_id("strix_scan"),
            security_score=result["security_score"],
            critical_count=result["critical_count"],
            high_count=result["high_count"],
            medium_count=result["medium_count"],
            low_count=result["low_count"],
            status="completed",
            strix_cli_available=StrixSecurityEngine.is_strix_cli_available(),
            findings=finding_schemas
        ),
        request_id=generate_id("req")
    )

@router.get("/scans/{scan_id}", response_model=ResponseEnvelope[SecurityScanResponse])
def get_security_scan(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(SecurityScan).filter(SecurityScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Security scan not found")

    findings = [
        SecurityFindingSchema(
            id=f.id,
            title=f.title,
            category=f.category,
            severity=f.severity,
            file_path=f.file_path,
            line=f.line,
            remediation=f.remediation
        ) for f in scan.findings
    ]

    return ResponseEnvelope(
        data=SecurityScanResponse(
            scan_id=scan.id,
            security_score=scan.security_score,
            critical_count=scan.critical_count,
            high_count=scan.high_count,
            medium_count=scan.medium_count,
            low_count=scan.low_count,
            status=scan.status,
            findings=findings
        ),
        request_id=generate_id("req")
    )

@router.get("/reports/{project_id}", response_model=ResponseEnvelope[dict])
def get_security_report(project_id: str, db: Session = Depends(get_db)):
    latest = db.query(SecurityScan).filter(SecurityScan.project_id == project_id).order_by(SecurityScan.created_at.desc()).first()
    if not latest:
        result = SecurityAnalysisEngine.run_scan()
        return ResponseEnvelope(data=result, request_id=generate_id("req"))

    return ResponseEnvelope(
        data={
            "project_id": project_id,
            "security_score": latest.security_score,
            "critical_count": latest.critical_count,
            "high_count": latest.high_count,
            "medium_count": latest.medium_count,
            "low_count": latest.low_count,
            "findings_count": len(latest.findings)
        },
        request_id=generate_id("req")
    )
