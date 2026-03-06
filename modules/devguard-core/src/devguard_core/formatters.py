from __future__ import annotations

import json
from datetime import datetime, timezone

from .models import ScanResult


def to_json(result: ScanResult) -> str:
    payload = {
        "total": result.total,
        "findings": [
            {
                "rule_id": f.rule_id,
                "severity": f.severity,
                "file_path": f.file_path,
                "line": f.line,
                "message": f.message,
                "recommendation": f.recommendation,
                "language": f.language,
                "confidence": f.confidence,
            }
            for f in result.findings
        ],
    }
    return json.dumps(payload, indent=2)


def to_sarif(result: ScanResult) -> str:
    rules = {}
    runs_results = []

    for finding in result.findings:
        rules[finding.rule_id] = {
            "id": finding.rule_id,
            "name": finding.rule_id,
            "shortDescription": {"text": finding.message},
            "help": {"text": finding.recommendation},
            "properties": {"severity": finding.severity, "confidence": finding.confidence},
        }
        runs_results.append(
            {
                "ruleId": finding.rule_id,
                "message": {"text": finding.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": finding.file_path},
                            "region": {"startLine": finding.line},
                        }
                    }
                ],
                "level": _to_sarif_level(finding.severity),
            }
        )

    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "devguard-core",
                        "version": "0.1.0",
                        "informationUri": "https://github.com/upendra-manike/developer-problem-solvers",
                        "rules": list(rules.values()),
                    }
                },
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "endTimeUtc": datetime.now(timezone.utc).isoformat(),
                    }
                ],
                "results": runs_results,
            }
        ],
    }
    return json.dumps(payload, indent=2)


def _to_sarif_level(severity: str) -> str:
    if severity == "high":
        return "error"
    if severity == "medium":
        return "warning"
    return "note"
