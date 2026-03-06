#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append release entry to changelog")
    parser.add_argument("--core-version", required=True)
    parser.add_argument("--ai-version", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    today = date.today().isoformat()

    entry = (
        f"## {today}\n\n"
        f"- devguard-core: {args.core_version}\n"
        f"- devguard-ai-validator: {args.ai_version}\n"
        f"- Automated release prep: version bump, checks, and packaging validation.\n\n"
    )

    if not CHANGELOG.exists():
        content = "# Changelog\n\n" + entry
    else:
        current = CHANGELOG.read_text(encoding="utf-8")
        content = current.rstrip() + "\n\n" + entry

    if args.dry_run:
        print(entry.strip())
        return 0

    CHANGELOG.write_text(content, encoding="utf-8")
    print(f"Updated {CHANGELOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
