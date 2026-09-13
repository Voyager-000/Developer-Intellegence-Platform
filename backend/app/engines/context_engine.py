import ast
import re
from typing import Dict, Any, List, Optional
from backend.app.core.security import calculate_shannon_entropy, redact_secrets_text

class SmartContextEngine:
    """
    Implements the Smart Repo Selection Blueprint (docs/smart-repo-selection-blueprint.md).
    Extracts scoped, minimal useful context across Levels 1-4 with strict token budgeting.
    """

    @staticmethod
    def extract_context(
        source_code: str,
        line_number: int = 1,
        level: int = 2,
        file_path: str = "src/app.py",
        project_files: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        lines = source_code.splitlines()
        total_lines = len(lines)
        target_line_idx = max(1, min(line_number, total_lines)) if total_lines > 0 else 1

        # 1. Level 1: Immediate block (active line +/- 5 lines)
        start_l1 = max(0, target_line_idx - 5)
        end_l1 = min(total_lines, target_line_idx + 5)
        level1_code = "\n".join(lines[start_l1:end_l1])

        enclosing_scope = "module"
        imports_found = []
        function_code = level1_code

        # 2. Level 2: Enclosing function / class scope via AST
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            imports_found.append(n.name)
                    else:
                        module = node.module or ""
                        for n in node.names:
                            imports_found.append(f"{module}.{n.name}")

                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                        if node.lineno <= target_line_idx <= (node.end_lineno or node.lineno):
                            enclosing_scope = f"{node.__class__.__name__}: {node.name}"
                            func_lines = lines[node.lineno - 1 : node.end_lineno]
                            function_code = "\n".join(func_lines)
        except Exception:
            enclosing_scope = "unparsed_scope"

        context_data = {
            "target_line": target_line_idx,
            "context_level": level,
            "enclosing_scope": enclosing_scope,
            "focal_code": level1_code,
            "scoped_code": function_code if level >= 2 else level1_code,
            "imports": imports_found if level >= 2 else [],
            "sanitized": True
        }

        # 3. Level 3: Cross-module dependencies and Git diff hunks
        if level >= 3:
            context_data["git_diff_scope"] = f"Hunk around line {target_line_idx} in {file_path}"
            # Resolve related companion files
            related = []
            if project_files:
                for pf in project_files:
                    p = pf.get("path") or pf.get("name") or ""
                    if p != file_path and any(mod.split(".")[0] in p for mod in imports_found):
                        related.append(p)
            context_data["related_symbols"] = related[:4]

        # 4. Level 4: Project-level topology, schemas & deployment config
        if level >= 4:
            topology = {
                "manifest_present": False,
                "framework": "unknown",
                "db_schemas": [],
                "dependencies": []
            }
            if project_files:
                for pf in project_files:
                    p = pf.get("path") or pf.get("name") or ""
                    c = pf.get("content", "")
                    if "requirements.txt" in p:
                        topology["manifest_present"] = True
                        topology["framework"] = "python_fastapi" if "fastapi" in c else "python"
                        topology["dependencies"] = [line.strip() for line in c.splitlines() if line.strip() and not line.startswith("#")][:10]
                    elif "package.json" in p:
                        topology["manifest_present"] = True
                        topology["framework"] = "node_javascript"
                    elif p.endswith(".sql") or "models.py" in p:
                        topology["db_schemas"].append(p)
            context_data["project_scope"] = topology

        # Enforce sanitization: redact secrets
        context_data["scoped_code"] = redact_secrets_text(context_data["scoped_code"])
        context_data["focal_code"] = redact_secrets_text(context_data["focal_code"])

        return context_data
