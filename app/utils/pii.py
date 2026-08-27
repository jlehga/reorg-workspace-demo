"""PII minimization helpers for prompts and audit metadata."""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
COMP_RE = re.compile(
    r"(?i)\b(salary|comp(?:ensation)?|bonus|equity|rsu|base pay)\b[^.\n]{0,40}"
)


def redact_for_prompt(text: str) -> str:
    """
    Minimize sensitive content before sending to an LLM.

    Prototype heuristic — production would use a dedicated DLP classifier
    and allowlists of fields permitted in model context.
    """
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    redacted = COMP_RE.sub("[REDACTED_COMPENSATION_MENTION]", redacted)
    return redacted


def mask_name(name: str) -> str:
    parts = name.split()
    if not parts:
        return "***"
    if len(parts) == 1:
        return parts[0][0] + "***"
    return f"{parts[0][0]}*** {parts[-1][0]}***"
