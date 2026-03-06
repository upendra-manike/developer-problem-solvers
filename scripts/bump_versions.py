#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_PYPROJECT = ROOT / "modules" / "devguard-core" / "pyproject.toml"
AI_PYPROJECT = ROOT / "modules" / "devguard-ai-validator" / "pyproject.toml"


@dataclass
class VersionState:
    core: str
    ai: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bump package versions for release")
    parser.add_argument("--part", choices=["major", "minor", "patch"], default="patch")
    parser.add_argument(
        "--package",
        choices=["devguard-core", "devguard-ai-validator", "both"],
        default="both",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    current = VersionState(
        core=read_version(CORE_PYPROJECT),
        ai=read_version(AI_PYPROJECT),
    )

    next_versions = VersionState(core=current.core, ai=current.ai)

    if args.package in {"devguard-core", "both"}:
        next_versions.core = bump_semver(current.core, args.part)
    if args.package in {"devguard-ai-validator", "both"}:
        next_versions.ai = bump_semver(current.ai, args.part)

    if args.package in {"devguard-core", "both"}:
        write_version(CORE_PYPROJECT, next_versions.core, dry_run=args.dry_run)

    if args.package in {"devguard-ai-validator", "both"}:
        write_version(AI_PYPROJECT, next_versions.ai, dry_run=args.dry_run)

    # Keep minimum dependency aligned when core changes.
    if args.package in {"devguard-core", "both"}:
        write_ai_core_dependency(AI_PYPROJECT, next_versions.core, dry_run=args.dry_run)

    print(f"core: {current.core} -> {next_versions.core}")
    print(f"ai-validator: {current.ai} -> {next_versions.ai}")
    if args.dry_run:
        print("mode: dry-run")
    return 0


def read_version(pyproject: Path) -> str:
    text = pyproject.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"(\d+\.\d+\.\d+)"\s*$', text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"Could not find version in {pyproject}")
    return match.group(1)


def write_version(pyproject: Path, version: str, dry_run: bool = False) -> None:
    text = pyproject.read_text(encoding="utf-8")
    new_text, count = re.subn(
        r'^(version\s*=\s*")(\d+\.\d+\.\d+)("\s*)$',
        rf"\g<1>{version}\g<3>",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"Expected one version field in {pyproject}")
    if not dry_run:
        pyproject.write_text(new_text, encoding="utf-8")


def write_ai_core_dependency(pyproject: Path, core_version: str, dry_run: bool = False) -> None:
    text = pyproject.read_text(encoding="utf-8")
    new_text, _ = re.subn(
        r'devguard-core>=\d+\.\d+\.\d+',
        f"devguard-core>={core_version}",
        text,
        count=1,
    )
    if not dry_run:
        pyproject.write_text(new_text, encoding="utf-8")


def bump_semver(version: str, part: str) -> str:
    major, minor, patch = [int(x) for x in version.split(".")]
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


if __name__ == "__main__":
    raise SystemExit(main())
