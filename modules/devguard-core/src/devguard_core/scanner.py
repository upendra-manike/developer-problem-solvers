from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .checks import SUPPORTED_EXTENSIONS, run_builtin_checks
from .config import ScanOptions
from .models import ScanResult


def iter_source_files(path: Path, options: ScanOptions) -> list[Path]:
    if path.is_file():
        try:
            if path.stat().st_size > options.max_file_size_bytes:
                return []
        except OSError:
            return []
        return [path]

    excluded_dirs = options.excluded_dirs
    files: list[Path] = []
    for ext in SUPPORTED_EXTENSIONS.keys():
        for file in path.rglob(f"*{ext}"):
            if any(part in excluded_dirs for part in file.parts):
                continue
            if file.is_symlink():
                continue
            try:
                if file.stat().st_size > options.max_file_size_bytes:
                    continue
            except OSError:
                continue
            files.append(file)
    return sorted(set(files))


def scan_path(path: Path, options: ScanOptions | None = None) -> ScanResult:
    return scan_targets([path], options=options)


def scan_targets(paths: list[Path], options: ScanOptions | None = None) -> ScanResult:
    opts = options or ScanOptions()
    files = _expand_paths(paths, opts)
    findings = []

    with ThreadPoolExecutor(max_workers=opts.workers) as executor:
        for result in executor.map(_scan_file, files):
            findings.extend(result)

    findings.sort(key=lambda f: (f.file_path, f.line, f.rule_id, f.message))
    return ScanResult(findings=findings)


def _scan_file(file: Path) -> list:
    try:
        text = file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        # Skip files with unsupported encoding or transient read errors.
        return []
    return run_builtin_checks(file, text)


def _expand_paths(paths: list[Path], options: ScanOptions) -> list[Path]:
    files: list[Path] = []
    supported_exts = set(SUPPORTED_EXTENSIONS.keys())
    for path in paths:
        if not path.exists():
            continue
        if path.is_dir():
            files.extend(iter_source_files(path, options))
            continue
        if path.suffix.lower() not in supported_exts:
            continue
        try:
            if path.stat().st_size > options.max_file_size_bytes:
                continue
        except OSError:
            continue
        files.append(path)
    return sorted(set(files))
