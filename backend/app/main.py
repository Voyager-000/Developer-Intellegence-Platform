import os
import re
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, Response
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
public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "public"))
webview_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "webview-ui"))


def _frontend_root() -> Optional[str]:
    candidates = [public_dir, react_dist]
    for root in candidates:
        if os.path.exists(os.path.join(root, "index.html")) and os.path.isdir(os.path.join(root, "assets")):
            return root
    for root in candidates:
        if os.path.exists(os.path.join(root, "index.html")):
            return root
    return None


frontend_root = _frontend_root()

if frontend_root and os.path.isdir(os.path.join(frontend_root, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_root, "assets")), name="react-assets")

for images_dir in (
    os.path.join(frontend_root, "images") if frontend_root else "",
    os.path.join(react_dist, "images"),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "images")),
):
    if images_dir and os.path.exists(images_dir):
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

def _frontend_index() -> Optional[str]:
    if frontend_root:
        index_path = os.path.join(frontend_root, "index.html")
        if os.path.exists(index_path):
            return index_path
    return None


@app.middleware("http")
async def allow_asset_cors(request: Request, call_next):
    if request.method == "OPTIONS" and request.url.path.startswith("/assets/"):
        return Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
            },
        )
    response = await call_next(request)
    if request.url.path.startswith("/assets/"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    return response


@app.get("/")
def serve_root():
    index_path = _frontend_index()
    if index_path:
        with open(index_path, "r", encoding="utf-8") as handle:
            html = handle.read()
        html = re.sub(r"\s+crossorigin(=\"[^\"]*\")?", "", html)
        return HTMLResponse(html)
    return {"message": "Developer Intelligence API Running"}
