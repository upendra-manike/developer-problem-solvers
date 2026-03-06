from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    description: str
    fix: str
    match_type: str = "regex"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    file_path: str
    line: int
    message: str
    recommendation: str
    language: str
    confidence: float

    def __post_init__(self) -> None:
        if self.severity not in {"low", "medium", "high"}:
            raise ValueError(f"Invalid severity: {self.severity}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Invalid confidence: {self.confidence}")
        if self.line <= 0:
            raise ValueError(f"Invalid line: {self.line}")


@dataclass(frozen=True)
class ScanResult:
    findings: list[Finding]

    @property
    def total(self) -> int:
        return len(self.findings)

    def relative_to(self, root: Path) -> "ScanResult":
        rel_findings: list[Finding] = []
        for f in self.findings:
            p = Path(f.file_path)
            rel_path = str(p.relative_to(root)) if p.is_absolute() and root in p.parents else f.file_path
            rel_findings.append(
                Finding(
                    rule_id=f.rule_id,
                    severity=f.severity,
                    file_path=rel_path,
                    line=f.line,
                    message=f.message,
                    recommendation=f.recommendation,
                    language=f.language,
                    confidence=f.confidence,
                )
            )
        return ScanResult(findings=rel_findings)
