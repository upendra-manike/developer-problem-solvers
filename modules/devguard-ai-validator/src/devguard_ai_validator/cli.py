from __future__ import annotations

import argparse
from pathlib import Path

from devguard_core.formatters import to_json, to_sarif
from devguard_core.scanner import scan_path


MIN_CONFIDENCE = 0.7


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DevGuard AI validator")
    parser.add_argument("target", help="Target file or directory")
    parser.add_argument("--format", choices=["json", "sarif"], default="json")
    parser.add_argument("--min-confidence", type=float, default=MIN_CONFIDENCE)
    parser.add_argument("--output", help="Output file path (optional)")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target = Path(args.target).resolve()

    result = scan_path(target)
    filtered = [f for f in result.findings if f.confidence >= args.min_confidence]

    from devguard_core.models import ScanResult

    filtered_result = ScanResult(findings=filtered)
    body = to_sarif(filtered_result) if args.format == "sarif" else to_json(filtered_result)

    if args.output:
        Path(args.output).write_text(body + "\n", encoding="utf-8")
    else:
        print(body)

    return 1 if filtered_result.total > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
