import os
import requests
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings

class TursoClient:
    """
    Direct Cloud Database integration for Turso (libSQL) via the HTTP Pipeline API.
    Supports queries, transactions, and schema migrations.
    """

    def __init__(self, db_url: Optional[str] = None, auth_token: Optional[str] = None):
        raw_url = db_url or settings.TURSO_DATABASE_URL or os.getenv("TURSO_DATABASE_URL", "")
        # Convert libsql:// to https://
        if raw_url.startswith("libsql://"):
            self.base_url = "https://" + raw_url[len("libsql://"):]
        else:
            self.base_url = raw_url

        self.pipeline_url = f"{self.base_url}/v2/pipeline"
        self.auth_token = auth_token or settings.TURSO_AUTH_TOKEN or os.getenv("TURSO_AUTH_TOKEN", "")

    def is_configured(self) -> bool:
        return bool(self.base_url and self.auth_token)

    def execute(self, sql: str, args: Optional[List[Any]] = None) -> Dict[str, Any]:
        if not self.is_configured():
            return {"error": "Turso credentials not configured"}

        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

        stmt: Dict[str, Any] = {"sql": sql}
        if args:
            stmt["args"] = [{"type": "text", "value": str(a)} for a in args]

        body = {
            "requests": [
                {"type": "execute", "stmt": stmt}
            ]
        }

        response = requests.post(self.pipeline_url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if results and results[0].get("type") == "ok":
            res_payload = results[0].get("response", {}).get("result", {})
            cols = [c["name"] for c in res_payload.get("cols", [])]
            raw_rows = res_payload.get("rows", [])
            parsed_rows = []
            for row in raw_rows:
                row_dict = {}
                for idx, col in enumerate(cols):
                    cell = row[idx]
                    row_dict[col] = cell.get("value") if isinstance(cell, dict) else cell
                parsed_rows.append(row_dict)
            return {
                "success": True,
                "rows": parsed_rows,
                "affected_row_count": res_payload.get("affected_row_count", 0),
                "duration_ms": res_payload.get("query_duration_ms", 0)
            }
        elif results and results[0].get("type") == "error":
            return {"success": False, "error": results[0].get("error", {}).get("message", "Query error")}

        return {"success": True, "rows": []}

    def init_schema(self) -> Dict[str, Any]:
        """Creates the Developer Intelligence tables on Turso cloud database."""
        table_statements = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT DEFAULT 'developer',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                owner_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS analysis_jobs (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                job_type TEXT DEFAULT 'code_analysis',
                status TEXT DEFAULT 'completed',
                total_findings INTEGER DEFAULT 0,
                critical_count INTEGER DEFAULT 0,
                high_count INTEGER DEFAULT 0,
                medium_count INTEGER DEFAULT 0,
                low_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS findings (
                id TEXT PRIMARY KEY,
                job_id TEXT,
                category TEXT NOT NULL,
                severity TEXT DEFAULT 'MEDIUM',
                confidence REAL DEFAULT 0.90,
                file_path TEXT NOT NULL,
                line INTEGER NOT NULL,
                column INTEGER DEFAULT 1,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                evidence TEXT,
                status TEXT DEFAULT 'open',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS database_analyses (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                overall_score INTEGER DEFAULT 72,
                slow_queries_count INTEGER DEFAULT 3,
                recommendations_count INTEGER DEFAULT 5,
                avg_response_time_ms REAL DEFAULT 184.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS security_scans (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                security_score INTEGER DEFAULT 92,
                critical_count INTEGER DEFAULT 0,
                high_count INTEGER DEFAULT 2,
                medium_count INTEGER DEFAULT 4,
                low_count INTEGER DEFAULT 7,
                status TEXT DEFAULT 'completed',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS deployment_validations (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                readiness_score INTEGER DEFAULT 87,
                decision TEXT DEFAULT 'REVIEW',
                warnings_count INTEGER DEFAULT 2,
                blockers_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                finding_id TEXT,
                fix_id TEXT,
                rating INTEGER DEFAULT 5,
                was_accepted INTEGER DEFAULT 1,
                user_comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]

        results = []
        for stmt in table_statements:
            res = self.execute(stmt.strip())
            results.append(res)

        return {"success": True, "tables_initialized": len(table_statements), "details": results}

    def sync_user(self, user_id: str, name: str, email: str, hashed_password: str, role: str = "developer"):
        if not self.is_configured():
            return None
        sql = """
        INSERT OR REPLACE INTO users (id, name, email, hashed_password, role)
        VALUES (?, ?, ?, ?, ?);
        """
        return self.execute(sql, [user_id, name, email, hashed_password, role])

    def sync_project(self, project_id: str, name: str, description: Optional[str] = None, owner_id: Optional[str] = None):
        if not self.is_configured():
            return None
        sql = """
        INSERT OR REPLACE INTO projects (id, name, description, owner_id)
        VALUES (?, ?, ?, ?);
        """
        return self.execute(sql, [project_id, name, description or "", owner_id or ""])

    def sync_analysis_job(self, job_id: str, project_id: str, total: int, crit: int, high: int, med: int, low: int, job_type: str = "code_analysis"):
        if not self.is_configured():
            return None
        sql = """
        INSERT OR REPLACE INTO analysis_jobs (id, project_id, job_type, total_findings, critical_count, high_count, medium_count, low_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        return self.execute(sql, [job_id, project_id, job_type, total, crit, high, med, low])

    def sync_finding(self, finding_id: str, job_id: str, category: str, severity: str, confidence: float,
                     file_path: str, line: int, col: int, title: str, description: str, evidence: str = ""):
        if not self.is_configured():
            return None
        sql = """
        INSERT OR REPLACE INTO findings (id, job_id, category, severity, confidence, file_path, line, column, title, description, evidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        return self.execute(sql, [finding_id, job_id, category, severity, confidence, file_path, line, col, title, description, evidence])

    def sync_database_analysis(self, id: str, project_id: str, score: int, slow_queries: int, recs: int, avg_time: float):
        if not self.is_configured():
            return None
        sql = """
        INSERT OR REPLACE INTO database_analyses (id, project_id, overall_score, slow_queries_count, recommendations_count, avg_response_time_ms)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        return self.execute(sql, [id, project_id, score, slow_queries, recs, avg_time])

    def sync_security_scan(self, id: str, project_id: str, score: int, crit: int, high: int, med: int, low: int):
        if not self.is_configured():
            return None
        sql = """
        INSERT OR REPLACE INTO security_scans (id, project_id, security_score, critical_count, high_count, medium_count, low_count)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        return self.execute(sql, [id, project_id, score, crit, high, med, low])

    def sync_deployment_validation(self, id: str, project_id: str, score: int, decision: str, warnings: int, blockers: int):
        if not self.is_configured():
            return None
        sql = """
        INSERT OR REPLACE INTO deployment_validations (id, project_id, readiness_score, decision, warnings_count, blockers_count)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        return self.execute(sql, [id, project_id, score, decision, warnings, blockers])

    def sync_feedback(self, id: str, finding_id: Optional[str], fix_id: Optional[str], rating: int, was_accepted: int, comment: Optional[str] = None):
        if not self.is_configured():
            return None
        sql = """
        INSERT OR REPLACE INTO feedback (id, finding_id, fix_id, rating, was_accepted, user_comment)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        return self.execute(sql, [id, finding_id or "", fix_id or "", rating, was_accepted, comment or ""])

    def get_cloud_status(self) -> Dict[str, Any]:
        """Returns Turso health, latency, and row counts."""
        if not self.is_configured():
            return {"configured": False, "status": "unconfigured"}

        try:
            ping_res = self.execute("SELECT 1 as ping;")
            latency_ms = ping_res.get("duration_ms", 0)

            tables = ["users", "projects", "analysis_jobs", "findings", "database_analyses", "security_scans", "deployment_validations", "feedback"]
            counts = {}
            for t in tables:
                r = self.execute(f"SELECT COUNT(*) as c FROM {t};")
                if r.get("success") and r.get("rows"):
                    counts[t] = int(r["rows"][0].get("c", 0))
                else:
                    counts[t] = 0

            return {
                "configured": True,
                "status": "connected",
                "database_url": self.base_url,
                "region": "aws-ap-south-1",
                "latency_ms": latency_ms,
                "tables": counts
            }
        except Exception as e:
            return {
                "configured": True,
                "status": "error",
                "database_url": self.base_url,
                "error": str(e)
            }

turso_client = TursoClient()
