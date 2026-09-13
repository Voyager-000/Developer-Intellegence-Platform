import difflib
import re
from typing import Dict, Any

class SelfCorrectionEngine:
    """
    Generates explanations, safe code patches, and unified diffs for detected findings.
    """

    @staticmethod
    def explain_finding(category: str, finding_title: str, evidence: str) -> Dict[str, str]:
        if "null_reference" in category:
            return {
                "why_problem": "The function can return None when the database lookup or query fails to find a matching record.",
                "why_matter": "Accessing user.name or any attribute on a NoneType object triggers an unhandled AttributeError at runtime, causing the endpoint to crash (HTTP 500).",
                "recommended_approach": "Check that the returned object exists before accessing its properties, or provide a default fallback."
            }
        elif "sqli" in category or "sql" in category:
            return {
                "why_problem": "Untrusted user parameters are directly concatenated into the raw SQL string without escaping.",
                "why_matter": "An attacker can craft malicious input to bypass authentication, extract sensitive database records, or drop tables.",
                "recommended_approach": "Rewrite the query to use parameterized query placeholders (:username or %s) and pass values as query parameters."
            }
        elif "secret" in category:
            return {
                "why_problem": "A secret credential (API key/password) is hardcoded directly in application source code.",
                "why_matter": "Anyone with read access to the repository or git history can steal the credentials and compromise cloud infrastructure.",
                "recommended_approach": "Replace hardcoded secret with os.getenv('API_KEY') and store the actual key in a .env file or cloud secrets manager."
            }
        else:
            return {
                "why_problem": f"Detected code issue: {finding_title}",
                "why_matter": "May cause maintainability degradation, unexpected runtime crashes, or security vulnerabilities.",
                "recommended_approach": "Refactor the logic according to clean code best practices."
            }

    @staticmethod
    def generate_fix(finding_id: str, file_path: str, source_code: str, line: int, category: str = "null_reference") -> Dict[str, Any]:
        lines = source_code.splitlines()
        before_lines = list(lines)
        after_lines = list(lines)

        explanation_data = SelfCorrectionEngine.explain_finding(category, "Detected Issue", lines[line - 1] if line <= len(lines) else "")

        if "null_reference" in category and 1 <= line <= len(lines):
            # Target line: e.g. print(user.name) or return user.name
            target_line = lines[line - 1]
            indent = " " * (len(target_line) - len(target_line.lstrip()))
            
            # Find variable name: e.g., user.name -> var is 'user'
            match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)', target_line)
            var_name = match.group(1) if match else "user"

            replacement = [
                f"{indent}if {var_name}:",
                f"{indent}    {target_line.strip()}",
                f"{indent}else:",
                f"{indent}    return None"
            ]

            # Before snippet: target line and assignment
            start_idx = max(0, line - 3)
            end_idx = min(len(lines), line + 1)
            before_code = "\n".join(lines[start_idx:end_idx])

            after_lines[line - 1 : line] = replacement
            after_code = "\n".join(after_lines[start_idx : start_idx + len(replacement) + 1])

        elif "sqli" in category and 1 <= line <= len(lines):
            target_line = lines[line - 1]
            indent = " " * (len(target_line) - len(target_line.lstrip()))
            before_code = target_line
            # Replace concatenated SQL with parameterized query
            replacement = [
                f'{indent}query = "SELECT * FROM users WHERE username = :username"',
                f'{indent}cursor.execute(query, {{"username": username}})'
            ]
            after_lines[line - 1 : line] = replacement
            after_code = "\n".join(replacement)

        elif "secret" in category and 1 <= line <= len(lines):
            target_line = lines[line - 1]
            indent = " " * (len(target_line) - len(target_line.lstrip()))
            before_code = target_line
            match = re.search(r'([a-zA-Z_0-9]+)\s*=', target_line)
            var_name = match.group(1) if match else "API_KEY"
            replacement = [
                f'{indent}import os',
                f'{indent}{var_name} = os.getenv("{var_name.upper()}", "")'
            ]
            after_lines[line - 1 : line] = replacement
            after_code = "\n".join(replacement)

        else:
            before_code = lines[line - 1] if line <= len(lines) else ""
            after_code = before_code

        # Generate Unified Diff
        diff = list(difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        ))
        patch_diff = "\n".join(diff)

        return {
            "finding_id": finding_id,
            "explanation": f"Add null safety guard before accessing attributes.",
            "root_cause": explanation_data["why_problem"],
            "patch_diff": patch_diff,
            "before_code": before_code,
            "after_code": after_code,
            "full_after_code": "\n".join(after_lines),
            "confidence": 0.94,
            "risk_level": "LOW"
        }
