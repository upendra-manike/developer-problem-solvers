from __future__ import annotations

from .models import Rule


BUILTIN_RULES: dict[str, Rule] = {
    "DG001": Rule(
        id="DG001",
        severity="high",
        description="Potential SQL injection via string concatenation in query execution.",
        fix="Use parameterized queries/placeholders instead of concatenation.",
    ),
    "DG002": Rule(
        id="DG002",
        severity="high",
        description="Potential unsafe deserialization call.",
        fix="Use safe loaders/whitelists and validate input before deserialization.",
    ),
    "DG003": Rule(
        id="DG003",
        severity="high",
        description="Potential hardcoded secret in source code.",
        fix="Move secrets to environment variables or a secrets manager.",
    ),
    "DG004": Rule(
        id="DG004",
        severity="medium",
        description="Potential inefficient object creation inside hot loops.",
        fix="Move expensive allocation/compilation outside loops or cache it.",
    ),
    "DG005": Rule(
        id="DG005",
        severity="medium",
        description="Network/async call without local error handling.",
        fix="Wrap risky network calls in try/except and handle expected failures.",
    ),
}
