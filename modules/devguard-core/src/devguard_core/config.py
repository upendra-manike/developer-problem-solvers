from __future__ import annotations

import os
from dataclasses import dataclass, field


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "dist",
    "build",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}


@dataclass(frozen=True)
class ScanOptions:
    excluded_dirs: set[str] = field(default_factory=lambda: set(DEFAULT_EXCLUDED_DIRS))
    max_file_size_bytes: int = 512 * 1024
    workers: int = max(1, min(32, (os.cpu_count() or 2) * 2))

    def __post_init__(self) -> None:
        if self.max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be > 0")
        if self.workers <= 0:
            raise ValueError("workers must be > 0")

    def merged_exclusions(self, extra: list[str] | None) -> set[str]:
        if not extra:
            return set(self.excluded_dirs)
        merged = set(self.excluded_dirs)
        merged.update(extra)
        return merged
