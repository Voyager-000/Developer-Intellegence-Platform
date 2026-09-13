import ast
import re
from typing import List, Dict, Any, Optional

class CodeIntelligenceEngine:
    """
    Analyzes Python, JavaScript, TypeScript, and source code for bugs,
    null references, memory leaks, high complexity, and unhandled exceptions.
    Returns normalized Finding objects.
    """

    @staticmethod
    def analyze_source(source_code: str, file_path: str = "src/app.py") -> List[Dict[str, Any]]:
        findings = []
        lines = source_code.splitlines()
        is_python = file_path.endswith(".py")
        is_js_ts = file_path.endswith((".js", ".ts", ".jsx", ".tsx"))

        # 1. Python AST-based checks
        if is_python:
            try:
                tree = ast.parse(source_code)
                class NullReferenceDetector(ast.NodeVisitor):
                    def __init__(self):
                        self.assignments = {} # var_name -> line

                    def visit_Assign(self, node):
                        if isinstance(node.value, ast.Call):
                            func_name = ""
                            curr = node.value
                            while isinstance(curr, ast.Call) and isinstance(curr.func, ast.Attribute):
                                func_name += " " + curr.func.attr
                                curr = curr.func.value
                            if isinstance(curr, ast.Call) and isinstance(curr.func, ast.Name):
                                func_name += " " + curr.func.id
                            elif isinstance(curr, ast.Name):
                                func_name += " " + curr.id

                            if any(k in func_name.lower() for k in ["get", "find", "lookup", "fetch", "auth", "first", "one", "filter"]):
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        self.assignments[target.id] = node.lineno
                        self.generic_visit(node)

                    def visit_Attribute(self, node):
                        if isinstance(node.value, ast.Name):
                            var_name = node.value.id
                            if var_name in self.assignments:
                                assign_line = self.assignments[var_name]
                                if node.lineno >= assign_line:
                                    findings.append({
                                        "category": "null_reference",
                                        "severity": "MEDIUM",
                                        "confidence": 0.94,
                                        "file_path": file_path,
                                        "line": node.lineno,
                                        "column": node.col_offset + 1,
                                        "title": "Potential null reference",
                                        "description": f"The returned object '{var_name}' may be undefined or None when lookup fails.",
                                        "evidence": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                                    })
                                    del self.assignments[var_name]
                        self.generic_visit(node)

                    def visit_AugAssign(self, node):
                        if isinstance(node.target, ast.Attribute) and isinstance(node.target.value, ast.Name):
                            var_name = node.target.value.id
                            if var_name in self.assignments:
                                findings.append({
                                    "category": "null_reference",
                                    "severity": "HIGH",
                                    "confidence": 0.95,
                                    "file_path": file_path,
                                    "line": node.lineno,
                                    "column": node.col_offset + 1,
                                    "title": "Potential null reference on mutation",
                                    "description": f"Mutating attribute '{node.target.attr}' on '{var_name}' which may be None when lookup fails.",
                                    "evidence": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                                })
                                del self.assignments[var_name]
                        self.generic_visit(node)

                NullReferenceDetector().visit(tree)

                # Unbounded Cache Growth (Memory Leak)
                for node in ast.walk(tree):
                    cache_var = None
                    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
                        for t in node.targets:
                            if isinstance(t, ast.Name) and "cache" in t.id.lower():
                                cache_var = t.id
                    elif isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Dict):
                        if isinstance(node.target, ast.Name) and "cache" in node.target.id.lower():
                            cache_var = node.target.id

                    if cache_var:
                        has_growth = False
                        for n in ast.walk(tree):
                            if isinstance(n, ast.Assign):
                                for sub_t in n.targets:
                                    if isinstance(sub_t, ast.Subscript) and isinstance(sub_t.value, ast.Name) and sub_t.value.id == cache_var:
                                        has_growth = True
                                        break
                        if has_growth:
                            findings.append({
                                "category": "memory_leak",
                                "severity": "HIGH",
                                "confidence": 0.91,
                                "file_path": file_path,
                                "line": node.lineno,
                                "column": 1,
                                "title": "Unbounded Cache Growth / Memory Leak Risk",
                                "description": f"Cache dictionary '{cache_var}' stores entries indefinitely without eviction, TTL, or max size limit.",
                                "evidence": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                            })

                # High Cyclomatic Complexity
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        branch_count = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.ExceptHandler)))
                        if branch_count > 6:
                            findings.append({
                                "category": "high_complexity",
                                "severity": "MEDIUM",
                                "confidence": 0.88,
                                "file_path": file_path,
                                "line": node.lineno,
                                "column": 1,
                                "title": "High Cyclomatic Complexity",
                                "description": f"Function '{node.name}' has cyclomatic complexity of {branch_count + 1}. Consider refactoring into smaller modular functions.",
                                "evidence": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                            })

            except SyntaxError as e:
                findings.append({
                    "category": "syntax_error",
                    "severity": "CRITICAL",
                    "confidence": 1.0,
                    "file_path": file_path,
                    "line": e.lineno or 1,
                    "column": e.offset or 1,
                    "title": "Syntax Error",
                    "description": str(e),
                    "evidence": e.text.strip() if e.text else ""
                })

        # 2. JavaScript / TypeScript semantic checks
        if is_js_ts:
            for idx, line in enumerate(lines, start=1):
                clean = line.strip()
                # Unchecked document.getElementById or querySelector
                if re.search(r'document\.(getElementById|querySelector)\([^)]+\)\.(value|click|style|addEventListener)', clean):
                    if "?." not in clean:
                        findings.append({
                            "category": "null_reference",
                            "severity": "MEDIUM",
                            "confidence": 0.92,
                            "file_path": file_path,
                            "line": idx,
                            "column": 1,
                            "title": "Unchecked DOM Query Return (Null Reference)",
                            "description": "Accessing property on DOM query result without null check or optional chaining (?.).",
                            "evidence": clean
                        })

                # Unhandled Promise rejection / missing catch
                if ".then(" in clean and ".catch(" not in clean and ";" in clean and "await" not in clean:
                    findings.append({
                        "category": "unhandled_exception",
                        "severity": "LOW",
                        "confidence": 0.85,
                        "file_path": file_path,
                        "line": idx,
                        "column": 1,
                        "title": "Promise Missing .catch() Handler",
                        "description": "Asynchronous promise chain without error handler can trigger UnhandledPromiseRejection.",
                        "evidence": clean
                    })

        # 3. Universal SQL Injection check in code
        for idx, line in enumerate(lines, start=1):
            if re.search(r'(SELECT|INSERT|UPDATE|DELETE).*(%s|\+|f[\'"]|\.format)', line, re.IGNORECASE):
                if not re.search(r':([a-zA-Z0-9_]+)', line):
                    findings.append({
                        "category": "security_sqli",
                        "severity": "CRITICAL",
                        "confidence": 0.97,
                        "file_path": file_path,
                        "line": idx,
                        "column": 1,
                        "title": "Potential SQL Injection",
                        "description": "SQL query is dynamically concatenated with user input. Use parameterized queries instead.",
                        "evidence": line.strip()
                    })

        return findings

    @staticmethod
    def analyze_codebase(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Runs Code Intelligence Engine analysis across all code files in the codebase.
        """
        all_findings = []
        for f in files:
            path = f.get("path") or f.get("name") or ""
            content = f.get("content", "")
            if not content:
                continue

            # Only analyze code files
            if path.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".sql")):
                file_findings = CodeIntelligenceEngine.analyze_source(content, path)
                all_findings.extend(file_findings)

        return all_findings
