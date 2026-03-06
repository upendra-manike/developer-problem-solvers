from __future__ import annotations

import ast
from pathlib import Path

from .models import Finding
from .rules import BUILTIN_RULES

SQL_PREFIXES = ("SELECT", "INSERT", "UPDATE", "DELETE")
SECRET_NAMES = {"api_key", "apikey", "secret", "token", "password", "access_token"}
UNSAFE_DESER_CALLS = {"pickle.loads", "yaml.load", "jsonpickle.decode"}


def run_python_ast_checks(file_path: Path, text: str) -> tuple[list[Finding], bool]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [], False

    findings: list[Finding] = []
    tainted_sql_vars: set[str] = set()

    for node in ast.walk(tree):
        finding = _detect_sql_injection(node, file_path, tainted_sql_vars)
        if finding is not None:
            findings.append(finding)

        finding = _detect_unsafe_deser(node, file_path)
        if finding is not None:
            findings.append(finding)

        finding = _detect_hardcoded_secrets(node, file_path)
        if finding is not None:
            findings.append(finding)

    return findings, True


def _detect_sql_injection(node: ast.AST, file_path: Path, tainted_sql_vars: set[str]) -> Finding | None:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        target_name = node.targets[0].id
        if _is_sql_concat(node.value):
            tainted_sql_vars.add(target_name)

    if not isinstance(node, ast.Call):
        return None

    call_name = _dotted_name(node.func)
    if call_name not in {"execute", "query", "cursor.execute", "cursor.query"}:
        return None
    if not node.args:
        return None

    first_arg = node.args[0]
    line = getattr(node, "lineno", 1)

    if isinstance(first_arg, ast.Name) and first_arg.id in tainted_sql_vars:
        return _make_finding(
            "DG001",
            file_path,
            line,
            "Potential SQL injection pattern found in query execution.",
            0.9,
        )

    if _is_sql_concat(first_arg):
        return _make_finding(
            "DG001",
            file_path,
            line,
            "Potential SQL injection pattern found in query construction.",
            0.91,
        )

    return None


def _detect_unsafe_deser(node: ast.AST, file_path: Path) -> Finding | None:
    if not isinstance(node, ast.Call):
        return None

    call_name = _dotted_name(node.func)
    if call_name in UNSAFE_DESER_CALLS:
        return _make_finding(
            "DG002",
            file_path,
            getattr(node, "lineno", 1),
            "Potential unsafe deserialization call detected.",
            0.92,
        )

    return None


def _detect_hardcoded_secrets(node: ast.AST, file_path: Path) -> Finding | None:
    if not isinstance(node, ast.Assign):
        return None
    if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
        return None

    var_name = node.targets[0].id.lower()
    if var_name not in SECRET_NAMES:
        return None

    value = node.value
    if isinstance(value, ast.Constant) and isinstance(value.value, str) and len(value.value) >= 8:
        return _make_finding(
            "DG003",
            file_path,
            getattr(node, "lineno", 1),
            "Potential hardcoded secret detected.",
            0.94,
        )

    return None


def _is_sql_concat(node: ast.AST) -> bool:
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Add):
        return False

    left = node.left
    if not isinstance(left, ast.Constant) or not isinstance(left.value, str):
        return False

    prefix = left.value.strip().upper()
    return prefix.startswith(SQL_PREFIXES)


def _dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = _dotted_name(node.value)
        return f"{left}.{node.attr}" if left else node.attr
    return ""


def _make_finding(rule_id: str, file_path: Path, line: int, message: str, confidence: float) -> Finding:
    rule = BUILTIN_RULES[rule_id]
    return Finding(
        rule_id=rule.id,
        severity=rule.severity,
        file_path=str(file_path),
        line=line,
        message=message,
        recommendation=rule.fix,
        language="python",
        confidence=confidence,
    )
