from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import ScanOptions
from .formatters import to_json, to_sarif
from .models import Finding, ScanResult
from .scanner import scan_path, scan_targets

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DevGuard core scanner")
    sub = parser.add_subparsers(dest="command", required=True)

    scan_cmd = sub.add_parser("scan", help="Scan a file or directory")
    scan_cmd.add_argument("target", help="Target file or directory")
    scan_cmd.add_argument("--file-list", help="Path to newline-delimited file list to scan")
    scan_cmd.add_argument("--format", choices=["json", "sarif"], default="json")
    scan_cmd.add_argument("--output", help="Output file path (optional)")
    scan_cmd.add_argument("--config", help="Path to .devguard.json config file")
    scan_cmd.add_argument("--exclude-dir", action="append", help="Directory name to exclude")
    scan_cmd.add_argument("--max-file-size-kb", type=int, help="Skip files larger than this size")
    scan_cmd.add_argument("--workers", type=int, help="Number of worker threads")
    scan_cmd.add_argument("--min-severity", choices=["low", "medium", "high"], help="Minimum severity to report")
    scan_cmd.add_argument("--min-confidence", type=float, help="Minimum confidence to report (0.0-1.0)")
    scan_cmd.add_argument("--include-rule", action="append", help="Only include matching rule ID (repeatable)")
    scan_cmd.add_argument("--exclude-rule", action="append", help="Exclude matching rule ID (repeatable)")
    scan_cmd.add_argument("--baseline-in", help="JSON file with known finding fingerprints to suppress")
    scan_cmd.add_argument("--baseline-out", help="Write current finding fingerprints to this JSON file")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        target = Path(args.target).resolve()
        if not target.exists():
            parser.error(f"Target does not exist: {target}")

        try:
            config = _load_config(args.config, target)
        except ValueError as exc:
            parser.error(str(exc))

        max_file_size_kb = _pick(args.max_file_size_kb, config, "max_file_size_kb", 512)
        workers = _pick(args.workers, config, "workers", ScanOptions().workers)
        min_severity = _pick(args.min_severity, config, "min_severity", "low")
        min_confidence = _pick(args.min_confidence, config, "min_confidence", 0.0)
        exclude_dirs = _pick_list(args.exclude_dir, config, "exclude_dir", [])
        include_rules = _normalized_rule_list(_pick_list(args.include_rule, config, "include_rule", []))
        exclude_rules = _normalized_rule_list(_pick_list(args.exclude_rule, config, "exclude_rule", []))
        baseline_in = _pick(args.baseline_in, config, "baseline_in", None)

        if max_file_size_kb <= 0:
            parser.error("--max-file-size-kb must be > 0")
        if workers <= 0:
            parser.error("--workers must be > 0")
        if not (0.0 <= min_confidence <= 1.0):
            parser.error("--min-confidence must be between 0.0 and 1.0")
        overlap = include_rules.intersection(exclude_rules)
        if overlap:
            parser.error(f"Rule IDs cannot be both included and excluded: {sorted(overlap)}")

        options = ScanOptions(
            excluded_dirs=ScanOptions().merged_exclusions(exclude_dirs),
            max_file_size_bytes=max_file_size_kb * 1024,
            workers=workers,
        )
        try:
            scan_list = _load_file_list(args.file_list)
        except ValueError as exc:
            parser.error(str(exc))
        if scan_list:
            result = scan_targets(scan_list, options=options)
        else:
            result = scan_path(target, options=options)
        baseline_root = target if target.is_dir() else target.parent
        normalized = result.relative_to(baseline_root)

        severity_filtered = _filter_by_min_severity(normalized, min_severity)
        confidence_filtered = _filter_by_min_confidence(severity_filtered, min_confidence)
        rule_filtered = _filter_by_rules(confidence_filtered, include_rules, exclude_rules)

        try:
            baseline = _load_baseline(baseline_in)
        except ValueError as exc:
            parser.error(str(exc))

        filtered_result = _filter_by_baseline(rule_filtered, baseline)

        if args.baseline_out:
            _write_baseline(args.baseline_out, rule_filtered)

        if args.format == "sarif":
            body = to_sarif(filtered_result)
        else:
            body = to_json(filtered_result)

        if args.output:
            Path(args.output).write_text(body + "\n", encoding="utf-8")
        else:
            print(body)

        # Non-zero exit when findings exist so it can gate CI.
        return 1 if filtered_result.total > 0 else 0

    parser.print_help()
    return 2


def _fingerprint(finding: Finding) -> str:
    return "|".join(
        [
            str(getattr(finding, "rule_id")),
            str(getattr(finding, "file_path")),
            str(getattr(finding, "line")),
            str(getattr(finding, "message")),
        ]
    )


def _load_baseline(path: str | None) -> set[str]:
    if not path:
        return set()
    baseline_file = Path(path)
    if not baseline_file.exists():
        return set()
    try:
        data = json.loads(baseline_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid baseline JSON in {baseline_file}: {exc.msg}") from exc
    if not isinstance(data, list):
        raise ValueError(f"Invalid baseline format in {baseline_file}: expected a JSON array")
    return {str(item) for item in data}


def _write_baseline(path: str, result: ScanResult) -> None:
    fingerprints = sorted({_fingerprint(f) for f in result.findings})
    Path(path).write_text(json.dumps(fingerprints, indent=2) + "\n", encoding="utf-8")


def _filter_by_baseline(result: ScanResult, baseline: set[str]) -> ScanResult:
    if not baseline:
        return result

    findings = [f for f in result.findings if _fingerprint(f) not in baseline]
    return ScanResult(findings=findings)


def _filter_by_min_severity(result: ScanResult, min_severity: str) -> ScanResult:
    threshold = SEVERITY_RANK[min_severity]
    findings = [f for f in result.findings if SEVERITY_RANK.get(f.severity, 0) >= threshold]
    return ScanResult(findings=findings)


def _filter_by_min_confidence(result: ScanResult, min_confidence: float) -> ScanResult:
    findings = [f for f in result.findings if f.confidence >= min_confidence]
    return ScanResult(findings=findings)


def _filter_by_rules(result: ScanResult, include_rules: set[str], exclude_rules: set[str]) -> ScanResult:
    findings = result.findings
    if include_rules:
        findings = [f for f in findings if f.rule_id.upper() in include_rules]
    if exclude_rules:
        findings = [f for f in findings if f.rule_id.upper() not in exclude_rules]
    return ScanResult(findings=findings)


def _load_config(path: str | None, target: Path) -> dict:
    config_path: Path | None = None
    if path:
        config_path = Path(path)
    else:
        root = target if target.is_dir() else target.parent
        candidate = root / ".devguard.json"
        if candidate.exists():
            config_path = candidate

    if config_path is None or not config_path.exists():
        return {}

    try:
        content = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid config JSON in {config_path}: {exc.msg}") from exc

    if not isinstance(content, dict):
        raise ValueError(f"Invalid config format in {config_path}: expected object")
    return content


def _pick(cli_value, config: dict, key: str, default):
    if cli_value is not None:
        return cli_value
    if key in config:
        return config[key]
    return default


def _pick_list(cli_value, config: dict, key: str, default: list[str]) -> list[str]:
    if cli_value is not None:
        return list(cli_value)
    if key in config:
        value = config[key]
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]
    return list(default)


def _normalized_rule_list(values: list[str]) -> set[str]:
    return {str(v).strip().upper() for v in values if str(v).strip()}


def _load_file_list(path: str | None) -> list[Path]:
    if not path:
        return []

    file_list = Path(path)
    if not file_list.exists():
        raise ValueError(f"File list does not exist: {file_list}")

    items: list[Path] = []
    for raw in file_list.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        p = Path(line)
        items.append(p if p.is_absolute() else Path.cwd() / p)
    return items


if __name__ == "__main__":
    raise SystemExit(main())
