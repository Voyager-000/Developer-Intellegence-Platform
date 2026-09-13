import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from backend.app.core.config import settings
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.models.entities import User, Project, generate_id
from backend.app.core.security import hash_password
from backend.app.api.v1 import api_v1_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed default demo user and project if missing
def seed_demo_data():
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "developer@example.com").first()
        if not demo_user:
            demo_user = User(
                id="usr_001",
                name="Lead Developer",
                email="developer@example.com",
                hashed_password=hash_password("password123"),
                role="developer"
            )
            db.add(demo_user)
            db.commit()

        demo_project = db.query(Project).filter(Project.id == "proj_001").first()
        if not demo_project:
            demo_project = Project(
                id="proj_001",
                name="Core Platform Service",
                description="Developer Intelligence Extension demonstration target repository",
                owner_id=demo_user.id
            )
            db.add(demo_project)
            db.commit()
    finally:
        db.close()

seed_demo_data()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "details": {}
            },
            "request_id": generate_id("err")
        }
    )

# Static UI serving: React Landing & Drag-Drop App + Extension Webview Dashboard
react_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
webview_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "webview-ui"))

if os.path.exists(os.path.join(react_dist, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(react_dist, "assets")), name="react-assets")

for images_dir in (
    os.path.join(react_dist, "images"),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "images")),
):
    if os.path.exists(images_dir):
        app.mount("/images", StaticFiles(directory=images_dir), name="hero-images")
        break

if os.path.exists(webview_dir):
    app.mount("/static", StaticFiles(directory=webview_dir), name="static")
    @app.get("/webview")
    def serve_webview():
        return FileResponse(os.path.join(webview_dir, "index.html"))
    @app.get("/dashboard")
    def serve_dashboard():
        return FileResponse(os.path.join(webview_dir, "index.html"))

@app.get("/")
def serve_root():
    if os.path.exists(os.path.join(react_dist, "index.html")):
        return FileResponse(os.path.join(react_dist, "index.html"))
    elif os.path.exists(os.path.join(webview_dir, "index.html")):
        return FileResponse(os.path.join(webview_dir, "index.html"))
    return {"message": "Developer Intelligence API Running"}
