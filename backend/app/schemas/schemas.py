from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")

class ResponseEnvelope(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[Dict[str, Any]] = None
    request_id: str = "req_default"

# Auth
class LoginRequest(BaseModel):
    email: Optional[str] = "admin@developer-intelligence.io"
    password: str

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    user: Dict[str, Any]

class RefreshRequest(BaseModel):
    refresh_token: str

# Project
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime

# Multi-file Codebase Data
class CodebaseFile(BaseModel):
    path: str
    content: str
    size: Optional[int] = None

# Code Analysis & Self-Correction
class CodeAnalysisRequest(BaseModel):
    project_id: Optional[str] = None
    file_path: str
    source_code: str
    language: str = "python"
    context_level: int = 2

class FindingSchema(BaseModel):
    id: str
    category: str
    severity: str
    confidence: float
    file_path: str
    line: int
    column: int
    title: str
    description: str
    evidence: Optional[str] = None
    status: str = "open"

class CodeAnalysisResponse(BaseModel):
    job_id: str
    findings: List[FindingSchema]
    total_findings: int
    summary: Dict[str, int]

class FixRequest(BaseModel):
    finding_id: str
    file_path: str
    source_code: str
    line: int

class FixResponse(BaseModel):
    fix_id: str
    finding_id: str
    explanation: str
    root_cause: str
    patch_diff: str
    before_code: str
    after_code: str
    confidence: float
    risk_level: str
    step_by_step_changes: List[str] = Field(default_factory=list)

class SmartRepoSelectRequest(BaseModel):
    query: str
    file_tree: List[str]
    context_level: int = 2

class SmartRepoSelectResponse(BaseModel):
    target_file: str
    companion_files: List[str]
    context_level: int
    reasoning: str

class FixValidationRequest(BaseModel):
    fix_id: str
    after_code: str
    language: str = "python"

class FixValidationResponse(BaseModel):
    fix_id: str
    syntax_check: bool
    compilation_check: bool
    unit_tests_pass: bool
    security_scan_pass: bool
    regression_test_pass: bool
    validation_score: float
    status: str
    details: Dict[str, Any]

class ApplyFixRequest(BaseModel):
    fix_id: str
    file_path: str
    applied_code: str

# Database Optimization
class DatabaseAnalysisRequest(BaseModel):
    project_id: Optional[str] = None
    query: Optional[str] = None
    files: Optional[List[CodebaseFile]] = None

class DatabaseFindingSchema(BaseModel):
    id: str
    query_name: str
    original_query: str
    optimized_query: Optional[str] = None
    execution_time_ms: float
    optimized_time_ms: Optional[float] = None
    impact: str
    recommendation: str
    index_suggestion: Optional[str] = None

class DatabaseAnalysisResponse(BaseModel):
    analysis_id: str
    overall_score: int
    slow_queries_count: int
    recommendations_count: int
    avg_response_time_ms: float
    has_database: bool = True
    message: Optional[str] = None
    findings: List[DatabaseFindingSchema]

class DatabaseOptimizeRequest(BaseModel):
    query: str

class DatabaseBenchmarkResponse(BaseModel):
    original_time_ms: float
    optimized_time_ms: float
    improvement_percent: float
    original_query: str
    optimized_query: str

# Security & Strix AI Integration
class SecurityScanRequest(BaseModel):
    project_id: Optional[str] = None
    file_path: Optional[str] = None
    source_code: Optional[str] = None
    files: Optional[List[CodebaseFile]] = None

class SecurityFindingSchema(BaseModel):
    id: str
    title: str
    category: str
    severity: str
    file_path: str
    line: int
    remediation: str
    poc_payload: Optional[str] = None
    cwe_id: Optional[str] = None
    attack_vector: Optional[str] = None

class SecurityScanResponse(BaseModel):
    scan_id: str
    security_score: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    status: str
    strix_cli_available: Optional[bool] = False
    findings: List[SecurityFindingSchema]

class StrixScanRequest(BaseModel):
    target_path: Optional[str] = None
    scan_mode: str = "quick" # quick, standard, deep
    files: Optional[List[CodebaseFile]] = None

# Deployment Validation
class DeploymentValidationRequest(BaseModel):
    project_id: Optional[str] = None
    include_benchmarks: bool = True

class DeploymentCheckSchema(BaseModel):
    pillar: str
    status: str # Passed, Warning, Failed
    details: str

class DeploymentValidationResponse(BaseModel):
    validation_id: str
    readiness_score: int
    decision: str # READY, REVIEW, BLOCKED
    warnings_count: int
    blockers_count: int
    code_quality_score: int
    security_score: int
    testing_score: int
    dependencies_score: int
    configuration_score: int
    performance_score: int
    checks: List[DeploymentCheckSchema]

# Project Health
class ProjectHealthSchema(BaseModel):
    score: int # 0 to 100
    grade: str # A+, A, B, C, D, F
    status_label: str
    open_issues_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    breakdown: Dict[str, int]

# Pipeline Stage Validation
class PipelineStageResult(BaseModel):
    stage_number: int
    name: str
    status: str # PASSED, FAILED, WARNING
    details: str
    score: float

class PipelineValidationRequest(BaseModel):
    project_id: Optional[str] = "project"
    files: Optional[List[CodebaseFile]] = None
    target_code: Optional[str] = None
    target_file_path: Optional[str] = None
    applied_patches_count: int = 0

class PipelineValidationResponse(BaseModel):
    validation_id: str
    composite_score: float
    composite_label: str
    decision: str # SAFE, REVIEW, BLOCKED
    stages: List[PipelineStageResult]

# Codebase End-to-End Pipeline
class CodebaseAnalysisRequest(BaseModel):
    project_id: Optional[str] = "project"
    files: List[CodebaseFile]

class CodebaseAnalysisResponse(BaseModel):
    project_id: str
    total_files: int
    project_health: ProjectHealthSchema
    code_findings: List[FindingSchema]
    security_findings: List[SecurityFindingSchema]
    database_analysis: DatabaseAnalysisResponse
    deployment_validation: DeploymentValidationResponse

# Feedback
class FeedbackCreate(BaseModel):
    finding_id: Optional[str] = None
    fix_id: Optional[str] = None
    rating: int = 5
    was_accepted: bool = True
    user_comment: Optional[str] = None
