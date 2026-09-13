import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List, Optional

# Load .env file from project root or backend folder
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Developer Intelligence Extension API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-Powered Code Quality • Database Optimization • Security Analysis • Deployment Validation"
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-developer-intelligence-sih-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database (SQLite / PostgreSQL / Turso)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./developer_intelligence.db")
    TURSO_DATABASE_URL: Optional[str] = os.getenv("TURSO_DATABASE_URL", None)
    TURSO_AUTH_TOKEN: Optional[str] = os.getenv("TURSO_AUTH_TOKEN", None)

    # OpenRouter AI Engine
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    OPENROUTER_FALLBACK_MODEL: str = os.getenv("OPENROUTER_FALLBACK_MODEL", "anthropic/claude-3.5-sonnet")
    
    # Feature Flags (from implementation plan Section 26)
    ENABLE_AI_FIXES: bool = True
    ENABLE_DB_OPTIMIZER: bool = True
    ENABLE_SECURITY_SCAN: bool = True
    ENABLE_DEPLOYMENT_VALIDATION: bool = True
    ENABLE_RAG: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        case_sensitive = True

settings = Settings()
