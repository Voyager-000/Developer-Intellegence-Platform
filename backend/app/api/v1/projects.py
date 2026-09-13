from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.entities import Project, generate_id
from backend.app.schemas.schemas import ProjectCreate, ProjectResponse, ResponseEnvelope

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ResponseEnvelope[ProjectResponse])
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    proj = Project(
        id=generate_id("proj"),
        name=project_in.name,
        description=project_in.description
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    from backend.app.core.turso import turso_client
    turso_client.sync_project(proj.id, proj.name, proj.description)
    return ResponseEnvelope(
        data=ProjectResponse(id=proj.id, name=proj.name, description=proj.description, created_at=proj.created_at),
        request_id=generate_id("req")
    )

@router.get("", response_model=ResponseEnvelope[List[ProjectResponse]])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    if not projects:
        # Default demo project
        demo = Project(id="proj_001", name="Developer Intelligence Sample", description="Core repository for demonstration")
        db.add(demo)
        db.commit()
        db.refresh(demo)
        projects = [demo]

    data = [ProjectResponse(id=p.id, name=p.name, description=p.description, created_at=p.created_at) for p in projects]
    return ResponseEnvelope(data=data, request_id=generate_id("req"))

@router.get("/{project_id}", response_model=ResponseEnvelope[ProjectResponse])
def get_project(project_id: str, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return ResponseEnvelope(
        data=ProjectResponse(id=proj.id, name=proj.name, description=proj.description, created_at=proj.created_at),
        request_id=generate_id("req")
    )
