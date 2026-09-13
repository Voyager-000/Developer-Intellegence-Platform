import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

class User(Base):
    __tablename__ = "users"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("usr"))
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(50), default="developer")
    auth_provider = Column(String(50), default="otp")
    login_count = Column(Integer, default=1)
    last_login_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

class LoginEvent(Base):
    __tablename__ = "login_events"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("log"))
    user_id = Column(String(50), nullable=True)
    username = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    auth_method = Column(String(50), default="otp")  # "otp", "google", "password", "admin_passcode"
    ip_address = Column(String(50), default="127.0.0.1")
    region = Column(String(100), default="Local / Cloud")
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Project(Base):
    __tablename__ = "projects"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("proj"))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(50), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="projects")
    repositories = relationship("Repository", back_populates="project", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="project", cascade="all, delete-orphan")
    security_scans = relationship("SecurityScan", back_populates="project", cascade="all, delete-orphan")
    deployment_validations = relationship("DeploymentValidation", back_populates="project", cascade="all, delete-orphan")

class Repository(Base):
    __tablename__ = "repositories"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("repo"))
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    repo_url = Column(String(255), nullable=True)
    branch = Column(String(100), default="main")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="repositories")

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("job"))
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=True)
    job_type = Column(String(50), default="code_analysis") # code_analysis, security, deployment
    status = Column(String(30), default="completed") # queued, running, completed, failed
    total_findings = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="analysis_jobs")
    findings = relationship("Finding", back_populates="job", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("find"))
    job_id = Column(String(50), ForeignKey("analysis_jobs.id"), nullable=True)
    category = Column(String(100), nullable=False) # null_reference, complexity, security_sqli, etc.
    severity = Column(String(20), default="MEDIUM") # CRITICAL, HIGH, MEDIUM, LOW
    confidence = Column(Float, default=0.90) # 0.00 to 1.00
    file_path = Column(String(255), nullable=False)
    line = Column(Integer, nullable=False)
    column = Column(Integer, default=1)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    status = Column(String(30), default="open") # open, fixed, ignored
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    job = relationship("AnalysisJob", back_populates="findings")
    fixes = relationship("Fix", back_populates="finding", cascade="all, delete-orphan")

class Fix(Base):
    __tablename__ = "fixes"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("fix"))
    finding_id = Column(String(50), ForeignKey("findings.id"), nullable=False)
    explanation = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    patch_diff = Column(Text, nullable=False) # unified diff representation
    before_code = Column(Text, nullable=False)
    after_code = Column(Text, nullable=False)
    confidence = Column(Float, default=0.95)
    risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH
    status = Column(String(30), default="generated") # generated, previewed, validated, applied, rolled_back
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    finding = relationship("Finding", back_populates="fixes")
    validation = relationship("FixValidation", back_populates="fix", uselist=False, cascade="all, delete-orphan")

class FixValidation(Base):
    __tablename__ = "fix_validations"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("val"))
    fix_id = Column(String(50), ForeignKey("fixes.id"), nullable=False)
    syntax_check = Column(Boolean, default=True)
    compilation_check = Column(Boolean, default=True)
    unit_tests_pass = Column(Boolean, default=True)
    security_scan_pass = Column(Boolean, default=True)
    regression_test_pass = Column(Boolean, default=True)
    validation_score = Column(Float, default=96.0)
    status = Column(String(30), default="passed") # passed, failed
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    fix = relationship("Fix", back_populates="validation")

class DatabaseAnalysis(Base):
    __tablename__ = "database_analyses"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("dba"))
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=True)
    overall_score = Column(Integer, default=72)
    slow_queries_count = Column(Integer, default=3)
    recommendations_count = Column(Integer, default=5)
    avg_response_time_ms = Column(Float, default=184.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    findings = relationship("DatabaseFinding", back_populates="analysis", cascade="all, delete-orphan")

class DatabaseFinding(Base):
    __tablename__ = "database_findings"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("dbf"))
    analysis_id = Column(String(50), ForeignKey("database_analyses.id"), nullable=False)
    query_name = Column(String(100), nullable=False)
    original_query = Column(Text, nullable=False)
    optimized_query = Column(Text, nullable=True)
    execution_time_ms = Column(Float, nullable=False)
    optimized_time_ms = Column(Float, nullable=True)
    impact = Column(String(20), default="HIGH") # HIGH, MEDIUM, LOW
    recommendation = Column(Text, nullable=False)
    index_suggestion = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    analysis = relationship("DatabaseAnalysis", back_populates="findings")

class SecurityScan(Base):
    __tablename__ = "security_scans"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("sec"))
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=True)
    security_score = Column(Integer, default=92)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=2)
    medium_count = Column(Integer, default=4)
    low_count = Column(Integer, default=7)
    status = Column(String(30), default="completed")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="security_scans")
    findings = relationship("SecurityFinding", back_populates="scan", cascade="all, delete-orphan")

class SecurityFinding(Base):
    __tablename__ = "security_findings"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("secf"))
    scan_id = Column(String(50), ForeignKey("security_scans.id"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False) # sql_injection, exposed_secret, vulnerable_dep
    severity = Column(String(20), default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    file_path = Column(String(255), nullable=False)
    line = Column(Integer, default=1)
    remediation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan = relationship("SecurityScan", back_populates="findings")

class DeploymentValidation(Base):
    __tablename__ = "deployment_validations"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("dep"))
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=True)
    readiness_score = Column(Integer, default=87)
    decision = Column(String(20), default="REVIEW") # READY, REVIEW, BLOCKED
    warnings_count = Column(Integer, default=2)
    blockers_count = Column(Integer, default=0)
    code_quality_score = Column(Integer, default=88)
    security_score = Column(Integer, default=91)
    testing_score = Column(Integer, default=82)
    dependencies_score = Column(Integer, default=94)
    configuration_score = Column(Integer, default=90)
    performance_score = Column(Integer, default=78)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="deployment_validations")
    checks = relationship("DeploymentCheck", back_populates="validation", cascade="all, delete-orphan")

class DeploymentCheck(Base):
    __tablename__ = "deployment_checks"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("depc"))
    validation_id = Column(String(50), ForeignKey("deployment_validations.id"), nullable=False)
    pillar = Column(String(50), nullable=False) # Build, Tests, Dependencies, Security, Configuration, Performance, Container
    status = Column(String(20), default="Passed") # Passed, Warning, Failed
    details = Column(Text, nullable=False)

    validation = relationship("DeploymentValidation", back_populates="checks")

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(String(50), primary_key=True, default=lambda: generate_id("fb"))
    finding_id = Column(String(50), nullable=True)
    fix_id = Column(String(50), nullable=True)
    rating = Column(Integer, default=5) # 1 to 5
    was_accepted = Column(Boolean, default=True)
    user_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
