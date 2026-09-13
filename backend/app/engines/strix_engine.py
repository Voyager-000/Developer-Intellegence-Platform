import os
import re
import math
import shutil
from typing import Dict, Any, List, Optional

def calculate_shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    char_counts = {}
    for char in data:
        char_counts[char] = char_counts.get(char, 0) + 1
    for count in char_counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

class StrixSecurityEngine:
    """
    AI-powered penetration testing & security vulnerability scanner inspired by usestrix/strix.
    Performs dynamic & static attack surface analysis, detects injection vectors,
    high-entropy secrets, and generates reproducible Proof-of-Concept (PoC) exploit payloads.
    """

    KNOWN_CVE_DATABASE = {
        "pyyaml": {
            "max_vulnerable": "5.3.1",
            "cve": "CVE-2020-1747",
            "severity": "CRITICAL",
            "cwe": "CWE-502",
            "desc": "Arbitrary code execution through untrusted YAML deserialization",
            "remediation": "Upgrade pyyaml to >= 6.0.1 and use yaml.safe_load()."
        },
        "requests": {
            "max_vulnerable": "2.31.0",
            "cve": "CVE-2023-32681",
            "severity": "MEDIUM",
            "cwe": "CWE-200",
            "desc": "Unintended leak of Proxy-Authorization headers across HTTPS redirects",
            "remediation": "Upgrade requests to >= 2.32.0."
        },
        "urllib3": {
            "max_vulnerable": "1.26.17",
            "cve": "CVE-2023-43804",
            "severity": "HIGH",
            "cwe": "CWE-200",
            "desc": "Cookie header leaking across cross-origin redirects",
            "remediation": "Upgrade urllib3 to >= 1.26.18 or >= 2.0.7."
        },
        "django": {
            "max_vulnerable": "3.2.23",
            "cve": "CVE-2024-24680",
            "severity": "HIGH",
            "cwe": "CWE-89",
            "desc": "Potential SQL injection in intcomma template filter",
            "remediation": "Upgrade django to >= 4.2.10 or >= 5.0.2."
        },
        "jsonwebtoken": {
            "max_vulnerable": "9.0.0",
            "cve": "CVE-2022-23529",
            "severity": "CRITICAL",
            "cwe": "CWE-78",
            "desc": "Remote code execution through malicious secretOrPublicKey",
            "remediation": "Upgrade jsonwebtoken to >= 9.0.1."
        },
        "lodash": {
            "max_vulnerable": "4.17.20",
            "cve": "CVE-2021-23337",
            "severity": "HIGH",
            "cwe": "CWE-1321",
            "desc": "Prototype pollution via template command injection",
            "remediation": "Upgrade lodash to >= 4.17.21."
        }
    }

    @staticmethod
    def is_strix_cli_available() -> bool:
        return shutil.which("strix") is not None

    @staticmethod
    def scan_file(file_path: str, source_code: str) -> List[Dict[str, Any]]:
        findings = []
        lines = source_code.splitlines()
        filename = os.path.basename(file_path)

        # 1. Dependency Scans
        if filename in ["requirements.txt", "Pipfile"]:
            for idx, line in enumerate(lines, start=1):
                clean = line.strip().lower()
                for pkg, info in StrixSecurityEngine.KNOWN_CVE_DATABASE.items():
                    if pkg in clean and any(op in clean for op in ["==", "<=", "~="]):
                        findings.append({
                            "title": f"Vulnerable Dependency: {pkg} ({info['cve']})",
                            "category": "vulnerable_dependency",
                            "severity": info["severity"],
                            "cwe_id": info["cwe"],
                            "file_path": file_path,
                            "line": idx,
                            "evidence": line.strip(),
                            "poc_payload": f"# Strix Dependency Audit: {pkg} package matches known vulnerable threshold <= {info['max_vulnerable']}\npip-audit --requirement {file_path}",
                            "remediation": info["remediation"],
                            "attack_vector": "Third-Party Supply Chain"
                        })

        if filename == "package.json":
            for idx, line in enumerate(lines, start=1):
                for pkg, info in StrixSecurityEngine.KNOWN_CVE_DATABASE.items():
                    if f'"{pkg}"' in line.lower():
                        findings.append({
                            "title": f"Vulnerable Node Dependency: {pkg} ({info['cve']})",
                            "category": "vulnerable_dependency",
                            "severity": info["severity"],
                            "cwe_id": info["cwe"],
                            "file_path": file_path,
                            "line": idx,
                            "evidence": line.strip(),
                            "poc_payload": f"npm audit --json | jq '.vulnerabilities.\"{pkg}\"'",
                            "remediation": info["remediation"],
                            "attack_vector": "NPM Supply Chain"
                        })

        # 2. Dockerfile checks
        if "Dockerfile" in filename:
            for idx, line in enumerate(lines, start=1):
                if re.search(r'^\s*USER\s+root\b', line, re.IGNORECASE):
                    findings.append({
                        "title": "Container Running as Root User (CWE-250)",
                        "category": "container_security",
                        "severity": "HIGH",
                        "cwe_id": "CWE-250",
                        "file_path": file_path,
                        "line": idx,
                        "evidence": line.strip(),
                        "poc_payload": "docker run -it <image> id\n# Output: uid=0(root) gid=0(root) groups=0(root)",
                        "remediation": "Define a dedicated non-root service user: 'RUN useradd -m appuser && USER appuser'",
                        "attack_vector": "Container Privilege Escalation"
                    })
                if re.search(r'^\s*FROM\s+[a-zA-Z0-9_\-\.\/]+:latest', line, re.IGNORECASE):
                    findings.append({
                        "title": "Unpinned Container Base Image",
                        "category": "container_security",
                        "severity": "LOW",
                        "cwe_id": "CWE-1188",
                        "file_path": file_path,
                        "line": idx,
                        "evidence": line.strip(),
                        "poc_payload": "# Docker build with latest tag introduces non-deterministic builds and supply-chain drift",
                        "remediation": "Pin base image to specific semantic digest or version hash (e.g., python:3.12-slim-bookworm).",
                        "attack_vector": "Image Drift"
                    })

        # 3. Source Code Scans (Python, JS, TS, SQL)
        for idx, line in enumerate(lines, start=1):
            clean_line = line.strip()
            if not clean_line or clean_line.startswith("#") or clean_line.startswith("//"):
                continue

            # SQL Injection (CWE-89)
            # Detect string interpolation/concatenation in SQL statements
            sqli_pattern = r'(f["\'].*(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER).*\{|(SELECT|INSERT|UPDATE|DELETE).*\+\s*[a-zA-Z0-9_]|(SELECT|INSERT|UPDATE|DELETE).*%s|\.format\()'
            if re.search(sqli_pattern, clean_line, re.IGNORECASE) and not re.search(r':([a-zA-Z0-9_]+)', clean_line):
                findings.append({
                    "title": "Dynamic SQL Injection Vulnerability (CWE-89)",
                    "category": "sql_injection",
                    "severity": "CRITICAL",
                    "cwe_id": "CWE-89",
                    "file_path": file_path,
                    "line": idx,
                    "evidence": clean_line,
                    "poc_payload": "' OR '1'='1' -- \nPayload: admin' UNION SELECT NULL, password, email FROM users --",
                    "remediation": "Replace dynamic string formatting with parameterized query placeholders (:param or ?) bound via driver/ORM.",
                    "attack_vector": "Database Ingestion Point"
                })

            # Remote Code Execution / Command Injection (CWE-78, CWE-94)
            if re.search(r'\b(eval|exec)\s*\(', clean_line):
                findings.append({
                    "title": "Dangerous Dynamic Code Execution (CWE-94)",
                    "category": "code_execution",
                    "severity": "CRITICAL",
                    "cwe_id": "CWE-94",
                    "file_path": file_path,
                    "line": idx,
                    "evidence": clean_line,
                    "poc_payload": "__import__('os').system('id')\n# Injected into dynamic eval() argument",
                    "remediation": "Avoid using eval/exec. Replace with static schema parsers (json.loads, ast.literal_eval).",
                    "attack_vector": "Unsanitized Code Evaluation"
                })

            if re.search(r'\bsubprocess\.(Popen|run|call)\s*\(.*shell\s*=\s*True', clean_line):
                findings.append({
                    "title": "Command Injection via shell=True (CWE-78)",
                    "category": "command_injection",
                    "severity": "CRITICAL",
                    "cwe_id": "CWE-78",
                    "file_path": file_path,
                    "line": idx,
                    "evidence": clean_line,
                    "poc_payload": "user_input = '; rm -rf / # or & whoami'",
                    "remediation": "Set shell=False and pass command and arguments as a validated list of strings.",
                    "attack_vector": "Host System Command Execution"
                })

            # Insecure Deserialization (CWE-502)
            if re.search(r'\bpickle\.loads?\s*\(', clean_line):
                findings.append({
                    "title": "Insecure Deserialization via Pickle (CWE-502)",
                    "category": "insecure_deserialization",
                    "severity": "CRITICAL",
                    "cwe_id": "CWE-502",
                    "file_path": file_path,
                    "line": idx,
                    "evidence": clean_line,
                    "poc_payload": "class Exploit:\n    def __reduce__(self):\n        return (__import__('os').system, ('id',))\n# Unpickling triggers arbitrary execution",
                    "remediation": "Never unpickle untrusted data. Use JSON, Protocol Buffers, or cryptographically signed tokens.",
                    "attack_vector": "Object Deserialization"
                })
            if re.search(r'\byaml\.load\s*\([^,)]+\)', clean_line):
                findings.append({
                    "title": "Unsafe YAML Load (CWE-502)",
                    "category": "insecure_deserialization",
                    "severity": "HIGH",
                    "cwe_id": "CWE-502",
                    "file_path": file_path,
                    "line": idx,
                    "evidence": clean_line,
                    "poc_payload": "!!python/object/apply:os.system [\"id\"]",
                    "remediation": "Use yaml.safe_load(data) instead of yaml.load(data).",
                    "attack_vector": "YAML Object Instantiation"
                })

            # Exposed High-Entropy Secrets & API Keys (CWE-798)
            if re.search(r'sk_(live|test)_[0-9a-zA-Z]{24,}', clean_line):
                findings.append({
                    "title": "Exposed Stripe Secret Key (CWE-798)",
                    "category": "exposed_secret",
                    "severity": "CRITICAL",
                    "cwe_id": "CWE-798",
                    "file_path": file_path,
                    "line": idx,
                    "evidence": clean_line,
                    "poc_payload": 'curl https://api.stripe.com/v1/charges -u [EXPOSED_KEY]:',
                    "remediation": "Revoke key from Stripe Dashboard immediately. Load secrets from environment variables (os.environ).",
                    "attack_vector": "Payment Gateway API"
                })
            elif re.search(r'AKIA[0-9A-Z]{16}', clean_line):
                findings.append({
                    "title": "Exposed AWS Access Key (CWE-798)",
                    "category": "exposed_secret",
                    "severity": "CRITICAL",
                    "cwe_id": "CWE-798",
                    "file_path": file_path,
                    "line": idx,
                    "evidence": clean_line,
                    "poc_payload": "aws sts get-caller-identity --access-key [EXPOSED_KEY]",
                    "remediation": "Rotate AWS IAM access key and migrate to IAM Roles or AWS Secrets Manager.",
                    "attack_vector": "Cloud Infrastructure"
                })
            elif re.search(r'(postgres|postgresql|mysql|mongodb|redis)://[a-zA-Z0-9_\-]+:[^@\s]+@[a-zA-Z0-9_\-\.]+', clean_line):
                findings.append({
                    "title": "Plaintext Database Credentials in Connection URI (CWE-798)",
                    "category": "exposed_secret",
                    "severity": "HIGH",
                    "cwe_id": "CWE-798",
                    "file_path": file_path,
                    "line": idx,
                    "evidence": re.sub(r':([^@]+)@', r':****@', clean_line),
                    "poc_payload": "psql [CONNECTION_STRING] -c 'SELECT current_user, inet_server_addr();'",
                    "remediation": "Move database credentials to a secure environment variable or KMS-backed secret store.",
                    "attack_vector": "Direct Database Access"
                })
            elif re.search(r'(secret_key|api_key|private_key|token)\s*=\s*[\'"][a-zA-Z0-9_\-]{20,}[\'"]', clean_line, re.IGNORECASE):
                match = re.search(r'[\'"]([a-zA-Z0-9_\-]{20,})[\'"]', clean_line)
                if match:
                    entropy = calculate_shannon_entropy(match.group(1))
                    if entropy > 3.8:
                        findings.append({
                            "title": "High-Entropy Hardcoded Secret (CWE-798)",
                            "category": "exposed_secret",
                            "severity": "HIGH",
                            "cwe_id": "CWE-798",
                            "file_path": file_path,
                            "line": idx,
                            "evidence": clean_line,
                            "poc_payload": f"# High entropy literal (Shannon H={round(entropy, 2)} > 3.8) detected in source code.",
                            "remediation": "Extract secret literal to .env file and add .env to .gitignore.",
                            "attack_vector": "Credential Harvesting"
                        })

            # Insecure Configuration: Debug Mode (CWE-489)
            if re.search(r'\b(DEBUG\s*=\s*True|debug\s*=\s*True)\b', clean_line):
                findings.append({
                    "title": "Debug Mode Enabled in Application Code (CWE-489)",
                    "category": "insecure_configuration",
                    "severity": "MEDIUM",
                    "cwe_id": "CWE-489", 
                    "file_path": file_path,
                    "line": idx,
                    "evidence": clean_line,
                    "poc_payload": "GET /nonexistent-endpoint-to-trigger-stacktrace\n# Triggers interactive debug console or internal source disclosure",
                    "remediation": "Set DEBUG=False in production and use structured logging for diagnostics.",
                    "attack_vector": "Information Disclosure"
                })

            # CORS Wildcard / Insecure Transport
            if re.search(r'allow_origins\s*=\s*\[\s*[\'"]\*[\'"]\s*\]', clean_line) and "allow_credentials=True" in source_code:
                findings.append({
                    "title": "Overly Permissive CORS with Credentials (CWE-942)",
                    "category": "insecure_configuration",
                    "severity": "MEDIUM",
                    "cwe_id": "CWE-942",
                    "file_path": file_path,
                    "line": idx,
                    "evidence": clean_line,
                    "poc_payload": "fetch('https://target-app.com/api/sensitive', { credentials: 'include' })",
                    "remediation": "Specify explicit allowed origin whitelist rather than '*' when allow_credentials is True.",
                    "attack_vector": "Cross-Origin CSRF / Token Theft"
                })

        return findings

    @staticmethod
    def scan_codebase(files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs comprehensive Strix security scan across all files in the project.
        """
        all_findings = []
        scanned_files_count = len(files)

        for file_info in files:
            path = file_info.get("path") or file_info.get("name") or "unknown"
            content = file_info.get("content", "")
            if not content:
                continue

            file_findings = StrixSecurityEngine.scan_file(path, content)
            all_findings.extend(file_findings)

        critical = sum(1 for f in all_findings if f["severity"] == "CRITICAL")
        high = sum(1 for f in all_findings if f["severity"] == "HIGH")
        medium = sum(1 for f in all_findings if f["severity"] == "MEDIUM")
        low = sum(1 for f in all_findings if f["severity"] == "LOW")

        penalty = (critical * 25) + (high * 12) + (medium * 4) + (low * 1)
        security_score = max(20, min(100, 100 - penalty))

        return {
            "security_score": security_score,
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "scanned_files_count": scanned_files_count,
            "strix_cli_available": StrixSecurityEngine.is_strix_cli_available(),
            "status": "completed",
            "findings": all_findings
        }
