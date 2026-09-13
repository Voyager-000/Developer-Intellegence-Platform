from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.engines.database_engine import DatabaseOptimizationEngine
from backend.app.models.entities import DatabaseAnalysis, DatabaseFinding, generate_id
from backend.app.schemas.schemas import (
    DatabaseAnalysisRequest, DatabaseAnalysisResponse, DatabaseFindingSchema,
    DatabaseOptimizeRequest, DatabaseBenchmarkResponse, ResponseEnvelope
)

router = APIRouter(prefix="/analysis/database", tags=["Database Optimization"])

@router.post("", response_model=ResponseEnvelope[DatabaseAnalysisResponse])
def analyze_database(req: DatabaseAnalysisRequest, db: Session = Depends(get_db)):
    file_dicts = [f.dict() for f in req.files] if req.files else None
    result = DatabaseOptimizationEngine.analyze_queries(req.query, files=file_dicts)

    dba_id = generate_id("dba")
    dba = DatabaseAnalysis(
        id=dba_id,
        project_id=req.project_id,
        overall_score=result["overall_score"],
        slow_queries_count=result["slow_queries_count"],
        recommendations_count=result["recommendations_count"],
        avg_response_time_ms=result["avg_response_time_ms"]
    )
    db.add(dba)

    finding_schemas = []
    for f in result["findings"]:
        dbf_id = generate_id("dbf")
        dbf = DatabaseFinding(
            id=dbf_id,
            analysis_id=dba_id,
            query_name=f["query_name"],
            original_query=f["original_query"],
            optimized_query=f.get("optimized_query"),
            execution_time_ms=f["execution_time_ms"],
            optimized_time_ms=f.get("optimized_time_ms"),
            impact=f["impact"],
            recommendation=f["recommendation"],
            index_suggestion=f.get("index_suggestion")
        )
        db.add(dbf)
        finding_schemas.append(DatabaseFindingSchema(
            id=dbf_id,
            query_name=f["query_name"],
            original_query=f["original_query"],
            optimized_query=f.get("optimized_query"),
            execution_time_ms=f["execution_time_ms"],
            optimized_time_ms=f.get("optimized_time_ms"),
            impact=f["impact"],
            recommendation=f["recommendation"],
            index_suggestion=f.get("index_suggestion")
        ))

    db.commit()

    # Sync to Turso cloud
    try:
        from backend.app.core.turso import turso_client
        if turso_client.is_configured():
            turso_client.sync_database_analysis(
                dba.id, dba.project_id or "default", dba.overall_score,
                dba.slow_queries_count, dba.recommendations_count, dba.avg_response_time_ms
            )
    except Exception:
        pass

    return ResponseEnvelope(
        data=DatabaseAnalysisResponse(
            analysis_id=dba_id,
            overall_score=result["overall_score"],
            slow_queries_count=result["slow_queries_count"],
            recommendations_count=result["recommendations_count"],
            avg_response_time_ms=result["avg_response_time_ms"],
            has_database=result.get("has_database", True),
            message=result.get("message"),
            findings=finding_schemas
        ),
        request_id=generate_id("req")
    )

@router.post("/optimize", response_model=ResponseEnvelope[DatabaseFindingSchema])
def optimize_query(req: DatabaseOptimizeRequest):
    finding = DatabaseOptimizationEngine.optimize_single_query(req.query)
    return ResponseEnvelope(
        data=DatabaseFindingSchema(
            id=generate_id("dbf"),
            query_name=finding["query_name"],
            original_query=finding["original_query"],
            optimized_query=finding.get("optimized_query"),
            execution_time_ms=finding["execution_time_ms"],
            optimized_time_ms=finding.get("optimized_time_ms"),
            impact=finding["impact"],
            recommendation=finding["recommendation"],
            index_suggestion=finding.get("index_suggestion")
        ),
        request_id=generate_id("req")
    )

@router.post("/benchmark", response_model=ResponseEnvelope[DatabaseBenchmarkResponse])
def benchmark_query(req: DatabaseOptimizeRequest):
    bench = DatabaseOptimizationEngine.benchmark(req.query)
    return ResponseEnvelope(
        data=DatabaseBenchmarkResponse(
            original_time_ms=bench["original_time_ms"],
            optimized_time_ms=bench["optimized_time_ms"],
            improvement_percent=bench["improvement_percent"],
            original_query=bench["original_query"],
            optimized_query=bench["optimized_query"]
        ),
        request_id=generate_id("req")
    )
