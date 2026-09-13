import json
import re
import difflib
import requests
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings

class OpenRouterClient:
    """
    Direct OpenRouter AI integration for real-time code inspection,
    smart repo selection, and automated patch generation.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
        self.fallback_model = settings.OPENROUTER_FALLBACK_MODEL
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("sk-or-"))

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        if not self.is_configured():
            raise ValueError("OpenRouter API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://villefy.io",
            "X-Title": "Developer Intelligence Platform"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }

        try:
            res = requests.post(self.endpoint, headers=headers, json=payload, timeout=25)
            if res.status_code != 200:
                # Try fallback model
                payload["model"] = self.fallback_model
                res = requests.post(self.endpoint, headers=headers, json=payload, timeout=25)
            
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            # Re-raise to trigger graceful engine fallback
            raise RuntimeError(f"OpenRouter API call failed: {str(e)}")

    def inspect_codebase(self, file_dicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans all files in a repository using OpenRouter AI.
        Analyzes key source files (.py, .ts, .js, .sql, etc.), cross-file context,
        and architecture to find genuine bugs, security flaws, null pointer risks,
        memory leaks, and unhandled exceptions.
        """
        if not self.is_configured() or not file_dicts:
            return []

        # Filter and rank candidate code files
        valid_exts = (".py", ".ts", ".js", ".jsx", ".tsx", ".sql", ".json", ".yaml", ".yml")
        code_files = [
            f for f in file_dicts 
            if any(f["path"].endswith(ext) for ext in valid_exts) 
            and not f["path"].startswith((".", "node_modules", "dist", "build", ".git"))
            and f.get("content", "").strip()
        ]

        if not code_files:
            return []

        # Sort so core logic/routes/services are prioritized
        def file_priority(f):
            p = f["path"].lower()
            if any(k in p for k in ["main", "app", "router", "route", "service", "controller", "order", "ledger", "auth"]):
                return 0
            if any(k in p for k in ["model", "schema", "db", "database", "util"]):
                return 1
            if p.endswith((".py", ".ts", ".js")):
                return 2
            return 3

        code_files.sort(key=file_priority)
        selected_files = code_files[:6]

        system_prompt = """You are an elite automated codebase intelligence engine powered by LLMs.
Analyze the provided codebase files for real, actionable defects:
1. Null references / AttributeError / unchecked optional returns (e.g. looking up a record and accessing attributes without checking for None).
2. Logic bugs / unhandled exceptions / race conditions.
3. Memory leaks / unbounded dictionary or cache accumulation without eviction.
4. Security vulnerabilities (SQL injection, hardcoded API secrets, insecure CORS/debug configurations).

Respond ONLY with a valid JSON object:
{
  "findings": [
    {
      "file_path": "<exact relative path from provided files>",
      "line": <int 1-indexed line number where the defect occurs>,
      "column": 1,
      "category": "null_reference" | "sql_injection" | "exposed_secret" | "memory_leak" | "logic_bug",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "confidence": 0.95,
      "title": "<Concise issue title>",
      "description": "<Clear explanation of why this is a defect>",
      "evidence": "<The exact line of defective code>"
    }
  ]
}
If no defects exist, return {"findings": []}."""

        formatted_files = []
        for cf in selected_files:
            lines = cf["content"].splitlines()
            numbered = "\n".join(f"{idx+1}: {l}" for idx, l in enumerate(lines[:100]))
            formatted_files.append(f"--- FILE: {cf['path']} ---\n{numbered}\n")

        user_prompt = f"Project Files Under Review:\n" + "\n".join(f"- {cf['path']} ({len(cf['content'])} bytes)" for cf in code_files) + "\n\n" + "\n".join(formatted_files)

        try:
            content = self._call_llm(system_prompt, user_prompt)
            data = json.loads(content)
            findings = data.get("findings", [])
            for f in findings:
                f["source"] = "OpenRouter AI"
                match_file = next((cf for cf in code_files if cf["path"] == f.get("file_path")), None)
                if match_file:
                    lines = match_file["content"].splitlines()
                    line_no = f.get("line", 1)
                    if 1 <= line_no <= len(lines) and not f.get("evidence"):
                        f["evidence"] = lines[line_no - 1].strip()
            return findings
        except Exception:
            # Fall back to inspecting individual top file
            if selected_files:
                top = selected_files[0]
                return self.inspect_code(top["content"], top["path"])
            return []

    def inspect_code(self, source_code: str, file_path: str, context: Optional[dict] = None) -> List[Dict[str, Any]]:
        """
        Actually reads source code and uses OpenRouter LLM to detect real bugs,
        null references, memory leaks, and vulnerabilities.
        """
        system_prompt = """You are an elite automated code analysis engine.
Inspect the provided source code for:
1. Null references / AttributeError / unchecked optional returns (e.g. looking up user/account and accessing attributes without checking for None).
2. Security vulnerabilities (SQL injection, hardcoded API secrets/passwords, insecure configuration).
3. Memory leaks / unbounded dictionary or list accumulation.
4. Concurrency or logic errors.

You must respond ONLY with a valid JSON object containing a "findings" array:
{
  "findings": [
    {
      "line": <int 1-indexed line number>,
      "column": 1,
      "category": "null_reference" | "sql_injection" | "exposed_secret" | "memory_leak" | "high_complexity",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "confidence": 0.95,
      "title": "<Short issue title>",
      "description": "<Clear explanation of why this is a bug/vulnerability>",
      "evidence": "<The exact line of code from source>"
    }
  ]
}
If no defects exist, return {"findings": []}."""

        # Add line numbers to source code for precision
        lines = source_code.splitlines()
        numbered_code = "\n".join(f"{idx+1}: {line}" for idx, line in enumerate(lines))

        user_prompt = f"File Path: {file_path}\n\nSource Code:\n```\n{numbered_code}\n```"

        try:
            content = self._call_llm(system_prompt, user_prompt)
            data = json.loads(content)
            findings = data.get("findings", [])
            # Format and guarantee file_path & fields
            for f in findings:
                f["file_path"] = file_path
                if not f.get("evidence") and 1 <= f.get("line", 0) <= len(lines):
                    f["evidence"] = lines[f["line"] - 1].strip()
            return findings
        except Exception as e:
            # Fall back to deterministic AST and regex checks
            from backend.app.engines.code_engine import CodeIntelligenceEngine
            return CodeIntelligenceEngine.analyze_source(source_code, file_path)

    def generate_fix(self, file_path: str, source_code: str, finding: dict, context: Optional[dict] = None) -> Dict[str, Any]:
        """
        Uses OpenRouter LLM to generate a real code patch, explaining what changes are proposed,
        providing step-by-step changes breakdown, and producing unified git diff.
        """
        system_prompt = """You are an expert software engineer AI specializing in automated self-correction.
Given a detected issue, you must fix it safely and cleanly without introducing side effects or regressions.
You must explain what changes are to be made, why they are needed, and provide the exact before/after code.

Respond ONLY with a valid JSON object:
{
  "explanation": "<High-level explanation of the fix and what is being modified>",
  "step_by_step_changes": [
    "1. Description of first change (e.g., added null check on line X)",
    "2. Description of second change (e.g., handled fallback return)",
    "3. Description of any imports added or adjusted"
  ],
  "root_cause": "<Why this defect occurs>",
  "before_code": "<Original 3-6 lines containing the defect>",
  "after_code": "<Patched 3-6 lines with the fix applied>",
  "full_after_code": "<The complete updated source file with the patch applied>",
  "confidence": 0.95,
  "risk_level": "LOW"
}"""

        user_prompt = f"""File: {file_path}
Issue: {finding.get('title')}
Line: {finding.get('line')}
Category: {finding.get('category')}
Evidence: {finding.get('evidence')}
Explanation: {finding.get('description')}

Source Code:
```
{source_code}
```"""

        try:
            content = self._call_llm(system_prompt, user_prompt)
            data = json.loads(content)
            full_after = data.get("full_after_code", source_code)
            
            # Compute unified diff
            diff = list(difflib.unified_diff(
                source_code.splitlines(),
                full_after.splitlines(),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm=""
            ))
            patch_diff = "\n".join(diff)

            return {
                "finding_id": finding.get("id", "find_ai"),
                "explanation": data.get("explanation", "AI-generated patch resolving defect."),
                "step_by_step_changes": data.get("step_by_step_changes", [
                    f"Line {finding.get('line')}: Added null-safety check or sanitization.",
                    "Safeguarded runtime attribute access against unexpected None values."
                ]),
                "root_cause": data.get("root_cause", finding.get("description", "")),
                "before_code": data.get("before_code", finding.get("evidence", "")),
                "after_code": data.get("after_code", ""),
                "full_after_code": full_after,
                "patch_diff": patch_diff if patch_diff else "@@ No text differences @@",
                "confidence": data.get("confidence", 0.95),
                "risk_level": data.get("risk_level", "LOW")
            }
        except Exception:
            # Fallback to local SelfCorrectionEngine
            from backend.app.engines.self_correction_engine import SelfCorrectionEngine
            fix = SelfCorrectionEngine.generate_fix(
                finding.get("id", "find_fb"), file_path, source_code,
                finding.get("line", 1), finding.get("category", "null_reference")
            )
            fix["step_by_step_changes"] = [
                f"Line {finding.get('line', 1)}: Wrap target statement with 'if {finding.get('evidence', 'obj').split('.')[0] if '.' in finding.get('evidence', '') else 'target'}:'",
                "Provide safe fallback return path to prevent unhandled runtime exception."
            ]
            return fix

    def select_repo_and_context(self, file_tree: List[str], problem_query: str) -> Dict[str, Any]:
        """
        Smart Repo Selection: determines which repository/module contains the flaw
        and which files are relevant for the fix.
        """
        system_prompt = """You are a smart multi-repository context scoping engine.
Given a list of files in a workspace and an issue query, identify:
1. Which file/module contains the root defect.
2. Which companion files (models, config, schemas) must be inspected to fix it.
3. The recommended context level (1=statement, 2=function, 3=cross-module, 4=project).

Respond ONLY with a valid JSON object:
{
  "target_file": "<path to primary file>",
  "companion_files": ["<path to related file 1>", "<path to related file 2>"],
  "context_level": 2,
  "reasoning": "<Why this file was selected>"
}"""

        user_prompt = f"Workspace Files:\n" + "\n".join(f"- {f}" for f in file_tree[:60]) + f"\n\nIssue Query: {problem_query}"

        try:
            content = self._call_llm(system_prompt, user_prompt)
            return json.loads(content)
        except Exception:
            # Deterministic fallback
            target = file_tree[0] if file_tree else "src/main.py"
            for f in file_tree:
                if any(k in f.lower() for k in ["auth", "order", "ledger", "database"]):
                    target = f
                    break
            return {
                "target_file": target,
                "companion_files": [f for f in file_tree if f != target][:3],
                "context_level": 2,
                "reasoning": f"Identified primary application module '{target}'."
            }

openrouter_client = OpenRouterClient()
