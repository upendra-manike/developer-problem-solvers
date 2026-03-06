from __future__ import annotations

import re
from pathlib import Path

from .ast_checks import run_python_ast_checks
from .models import Finding
from .rules import BUILTIN_RULES

SQL_INJECTION_PATTERN = re.compile(r"(?:execute|query)\s*\([^\n]*[\"'][^\"']*[\"']\s*\+", re.IGNORECASE)
SQL_ASSIGN_CONCAT_PATTERN = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*[\"']\s*(SELECT|INSERT|UPDATE|DELETE)\b[^\"']*[\"']\s*\+",
    re.IGNORECASE,
)
EXECUTE_VAR_PATTERN = re.compile(r"(?:execute|query)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)", re.IGNORECASE)
UNSAFE_DESER_PATTERN = re.compile(
    r"pickle\.loads\(|yaml\.load\(|ObjectInputStream\(|BinaryFormatter|jsonpickle\.decode\(",
    re.IGNORECASE,
)
HARDCODED_SECRET_PATTERN = re.compile(
    r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"'][A-Za-z0-9_\-\./+=]{8,}[\"']"
)
LOOP_HEADER_PATTERN = re.compile(r"^\s*(for|while)\b")
EXPENSIVE_IN_LOOP_PATTERN = re.compile(r"(re\.compile\(|new\s+Regex\(|json\.loads\(|datetime\.strptime\()")
ASYNC_DEF_PATTERN = re.compile(r"^\s*async\s+def\b")
NETWORK_CALL_PATTERN = re.compile(r"\b(requests\.|httpx\.|aiohttp\.|fetch\(|axios\.)")
TRY_PATTERN = re.compile(r"^\s*try\s*:")
IGNORE_INLINE_PATTERN = re.compile(r"devguard-ignore\s*:\s*(.+)", re.IGNORECASE)
IGNORE_NEXT_LINE_PATTERN = re.compile(r"devguard-ignore-next-line\s*:\s*(.+)", re.IGNORECASE)


SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
}


def detect_language(path: Path) -> str:
    return SUPPORTED_EXTENSIONS.get(path.suffix.lower(), "unknown")


def _make_finding(
    rule_id: str,
    file_path: Path,
    line: int,
    language: str,
    message: str,
    confidence: float,
) -> Finding:
    rule = BUILTIN_RULES[rule_id]
    return Finding(
        rule_id=rule.id,
        severity=rule.severity,
        file_path=str(file_path),
        line=line,
        message=message,
        recommendation=rule.fix,
        language=language,
        confidence=confidence,
    )


def run_builtin_checks(file_path: Path, text: str) -> list[Finding]:
    language = detect_language(file_path)
    findings: list[Finding] = []
    lines = text.splitlines()
    ast_parsed = False
    if language == "python":
        ast_findings, ast_parsed = run_python_ast_checks(file_path, text)
        findings.extend(ast_findings)

    tainted_sql_vars: set[str] = set()
    for idx, line in enumerate(lines, start=1):
        if language == "python" and ast_parsed:
            continue

        assign_match = SQL_ASSIGN_CONCAT_PATTERN.search(line)
        if assign_match:
            tainted_sql_vars.add(assign_match.group(1))

        if SQL_INJECTION_PATTERN.search(line):
            findings.append(
                _make_finding(
                    "DG001",
                    file_path,
                    idx,
                    language,
                    "Potential SQL injection pattern found in query construction.",
                    0.88,
                )
            )

        exec_match = EXECUTE_VAR_PATTERN.search(line)
        if exec_match and exec_match.group(1) in tainted_sql_vars:
            findings.append(
                _make_finding(
                    "DG001",
                    file_path,
                    idx,
                    language,
                    "Potential SQL injection pattern found in query execution.",
                    0.84,
                )
            )

        if UNSAFE_DESER_PATTERN.search(line):
            findings.append(
                _make_finding(
                    "DG002",
                    file_path,
                    idx,
                    language,
                    "Potential unsafe deserialization call detected.",
                    0.87,
                )
            )

        if HARDCODED_SECRET_PATTERN.search(line):
            findings.append(
                _make_finding(
                    "DG003",
                    file_path,
                    idx,
                    language,
                    "Potential hardcoded secret detected.",
                    0.91,
                )
            )

    findings.extend(_detect_expensive_allocations_in_loops(file_path, language, lines))
    findings.extend(_detect_network_calls_without_local_try(file_path, language, lines))
    deduped = _dedupe_findings(findings)
    return _apply_suppressions(deduped, lines)


def _dedupe_findings(findings: list[Finding]) -> list[Finding]:
    deduped: list[Finding] = []
    seen: set[tuple[str, str, int, str]] = set()
    for finding in findings:
        key = (finding.rule_id, finding.file_path, finding.line, finding.message)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def _detect_expensive_allocations_in_loops(file_path: Path, language: str, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for idx, line in enumerate(lines, start=1):
        if LOOP_HEADER_PATTERN.search(line):
            end = min(len(lines), idx + 6)
            for look_ahead in range(idx, end):
                if EXPENSIVE_IN_LOOP_PATTERN.search(lines[look_ahead - 1]):
                    findings.append(
                        _make_finding(
                            "DG004",
                            file_path,
                            look_ahead,
                            language,
                            "Potential repeated expensive allocation inside loop.",
                            0.72,
                        )
                    )
                    break
    return findings


def _detect_network_calls_without_local_try(file_path: Path, language: str, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for idx, line in enumerate(lines, start=1):
        if ASYNC_DEF_PATTERN.search(line):
            block_end = min(len(lines), idx + 20)
            block = lines[idx - 1:block_end]
            has_try = any(TRY_PATTERN.search(item) for item in block)
            for local_idx, block_line in enumerate(block, start=idx):
                if NETWORK_CALL_PATTERN.search(block_line) and not has_try:
                    findings.append(
                        _make_finding(
                            "DG005",
                            file_path,
                            local_idx,
                            language,
                            "Async/network call found without local try/except handling.",
                            0.68,
                        )
                    )
                    break
    return findings


def _apply_suppressions(findings: list[Finding], lines: list[str]) -> list[Finding]:
    line_suppressions, file_suppressions = _collect_suppressions(lines)
    filtered: list[Finding] = []
    for finding in findings:
        if "all" in file_suppressions or finding.rule_id in file_suppressions:
            continue
        suppressed = line_suppressions.get(finding.line, set())
        if "all" in suppressed or finding.rule_id in suppressed:
            continue
        filtered.append(finding)
    return filtered


def _collect_suppressions(lines: list[str]) -> tuple[dict[int, set[str]], set[str]]:
    line_suppressions: dict[int, set[str]] = {}
    file_suppressions: set[str] = set()

    for idx, line in enumerate(lines, start=1):
        next_match = IGNORE_NEXT_LINE_PATTERN.search(line)
        if next_match:
            rules = _parse_rule_list(next_match.group(1))
            line_suppressions.setdefault(idx + 1, set()).update(rules)

        inline_match = IGNORE_INLINE_PATTERN.search(line)
        if inline_match:
            rules = _parse_rule_list(inline_match.group(1))
            line_suppressions.setdefault(idx, set()).update(rules)
            if "file" in rules:
                file_suppressions.update({"all"})

    return line_suppressions, file_suppressions


def _parse_rule_list(raw: str) -> set[str]:
    # Accept comma or whitespace delimited rule IDs.
    items = [token.strip().upper() for token in re.split(r"[,\s]+", raw.strip()) if token.strip()]
    normalized = set(items)
    if "ALL" in normalized:
        return {"all"}
    if "FILE" in normalized:
        return {"file"}
    return normalized
