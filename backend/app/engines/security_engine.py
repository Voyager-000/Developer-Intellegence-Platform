import re
from typing import Dict, Any, List, Optional
from backend.app.engines.strix_engine import StrixSecurityEngine

class SecurityAnalysisEngine:
    """
    Unified SAST vulnerability detection, high-entropy secret scanning,
    dependency CVE scanner, and Strix AI penetration testing integration.
    """

    @staticmethod
    def run_scan(source_code: Optional[str] = None, file_path: str = "src/app.py") -> Dict[str, Any]:
        if not source_code:
            return {
                "security_score": 100,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "status": "completed",
                "findings": []
            }

        # Leverage StrixSecurityEngine for deep multi-vector scanning & PoC generation
        findings = StrixSecurityEngine.scan_file(file_path, source_code)

        critical = sum(1 for f in findings if f["severity"] == "CRITICAL")
        high = sum(1 for f in findings if f["severity"] == "HIGH")
        medium = sum(1 for f in findings if f["severity"] == "MEDIUM")
        low = sum(1 for f in findings if f["severity"] == "LOW")

        penalty = (critical * 25) + (high * 10) + (medium * 4) + (low * 1)
        score = max(20, min(100, 100 - penalty))

        return {
            "security_score": score,
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "status": "completed",
            "findings": findings
        }

    @staticmethod
    def run_codebase_scan(files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scans an entire list of codebase files through the Strix security suite.
        """
        return StrixSecurityEngine.scan_codebase(files)
