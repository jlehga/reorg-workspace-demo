"""LLM provider abstraction for structured reorg extraction."""

from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.models.extraction import (
    Ambiguity,
    ClaimedApproval,
    CostCenterChange,
    ExceptionMove,
    ExtractedRequest,
    ManagerChange,
    OrgChange,
    PersonRef,
)
from app.models.enums import ValidationSeverity
from app.utils.pii import redact_for_prompt

EXTRACTION_SCHEMA_HINT = """
Return ONLY valid JSON matching this schema:
{
  "effective_date": "YYYY-MM-DD or null",
  "summary": "one sentence",
  "people": [{"name": str, "role_hint": str|null}],
  "org_changes": [{"team_name": str, "from_org_or_manager": str|null, "to_org_or_manager": str|null, "expected_headcount": int|null}],
  "manager_changes": [{"subject_name": str, "from_manager": str|null, "to_manager": str|null, "subject_is_team": bool}],
  "cost_center_changes": [{"subject_name": str, "from_cost_center": str|null, "to_cost_center": str|null, "subject_type": "team"|"employee"}],
  "exceptions": [{"person_name": str, "to_org_or_manager": str|null, "to_manager": str|null, "to_cost_center": str|null, "notes": str|null}],
  "claimed_approvals": [{"approver_role_or_name": str, "claim_text": str}],
  "ambiguities": [{"field": str, "description": str, "severity": "info"|"warning"|"error"}],
  "assumptions": [str],
  "confidence": float
}
Rules:
- Do NOT treat natural-language approval claims as verified.
- Surface ambiguities instead of guessing.
- Preserve exception moves separately from the default team move.
"""


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def extract(self, raw_text: str) -> ExtractedRequest:
        raise NotImplementedError


class DeterministicExtractor(LLMProvider):
    """
    Deterministic structured extractor for demo/offline use.

    Used when no API key is configured. Produces schema-valid ExtractedRequest
    objects for the known scenarios and a best-effort parse otherwise.
    Explicitly NOT a substitute for production LLM interpretation quality —
    it exists so the demo path remains runnable without credentials.
    """

    name = "deterministic-demo"

    def extract(self, raw_text: str) -> ExtractedRequest:
        text = raw_text.strip()
        lower = text.lower()

        effective = _parse_date(text)
        people: list[PersonRef] = []
        for name in _find_names(text):
            people.append(PersonRef(name=name))

        org_changes: list[OrgChange] = []
        manager_changes: list[ManagerChange] = []
        cost_center_changes: list[CostCenterChange] = []
        exceptions: list[ExceptionMove] = []
        claimed: list[ClaimedApproval] = []
        ambiguities: list[Ambiguity] = []
        assumptions: list[str] = []

        # Team move pattern: move X from A to B
        team_match = re.search(
            r"move\s+(?:the\s+)?([A-Za-z0-9 &\-]+?)\s+(?:team\s+)?from\s+([A-Za-z .]+?)(?:'s organization)?\s+to\s+([A-Za-z .]+?)[\.\n]",
            text,
            re.IGNORECASE,
        )
        if not team_match:
            team_match = re.search(
                r"move\s+(?:the\s+)?([A-Za-z0-9 &\-]+?)\s+from\s+([A-Za-z .]+?)\s+to\s+([A-Za-z .]+?)[\.\n]",
                text,
                re.IGNORECASE,
            )

        team_name = None
        if team_match:
            team_name = team_match.group(1).strip().rstrip(".")
            if not team_name.lower().endswith("engineering") and "team" not in team_name.lower():
                # keep as-is; validation will resolve
                pass
            from_mgr = team_match.group(2).strip().rstrip(".")
            to_mgr = team_match.group(3).strip().rstrip(".")
            # Clean trailing phrases like "Finance has"
            to_mgr = re.split(r"\.\s+|,\s+(?:The|Finance|All|Also)", to_mgr)[0].strip()
            from_mgr = from_mgr.replace("'s organization", "").strip()

            headcount = _parse_headcount(text)
            org_changes.append(
                OrgChange(
                    team_name=team_name,
                    from_org_or_manager=from_mgr,
                    to_org_or_manager=to_mgr,
                    expected_headcount=headcount,
                )
            )
            manager_changes.append(
                ManagerChange(
                    subject_name=team_name,
                    from_manager=from_mgr,
                    to_manager=to_mgr,
                    subject_is_team=True,
                )
            )
            assumptions.append(
                f"Interpreted '{from_mgr}' / '{to_mgr}' as org/manager references for '{team_name}'."
            )

        # Cost center pattern
        cc_match = re.search(
            r"(?:from\s+cost\s+center\s+)?(CC-\d+)\s+to\s+(CC-\d+)",
            text,
            re.IGNORECASE,
        )
        if not cc_match:
            cc_match = re.search(
                r"cost\s+center\s+(CC-\d+)",
                text,
                re.IGNORECASE,
            )
            if cc_match and team_name:
                cost_center_changes.append(
                    CostCenterChange(
                        subject_name=team_name,
                        from_cost_center=None,
                        to_cost_center=cc_match.group(1).upper(),
                        subject_type="team",
                    )
                )
                ambiguities.append(
                    Ambiguity(
                        field="from_cost_center",
                        description="Source specifies destination cost center only.",
                        severity=ValidationSeverity.WARNING,
                    )
                )
        else:
            subject = team_name or "unknown team"
            cost_center_changes.append(
                CostCenterChange(
                    subject_name=subject,
                    from_cost_center=cc_match.group(1).upper(),
                    to_cost_center=cc_match.group(2).upper(),
                    subject_type="team",
                )
            )

        # Exception: Person will instead move to X under Y
        exc_match = re.search(
            r"([A-Z][a-z]+ [A-Z][a-z]+)\s+will instead move to\s+([A-Za-z ]+?)(?:\s+under\s+([A-Z][a-z]+ [A-Z][a-z]+))?",
            text,
        )
        if exc_match:
            exceptions.append(
                ExceptionMove(
                    person_name=exc_match.group(1),
                    to_org_or_manager=exc_match.group(2).strip(),
                    to_manager=exc_match.group(3),
                    notes="Exception to default team move",
                )
            )

        # Unknown manager / ledger team extras for scenario B
        unknown_mgr = re.search(
            r"under an unknown manager named\s+([A-Z][a-z]+ [A-Z][a-z]+)",
            text,
            re.IGNORECASE,
        )
        if unknown_mgr:
            mgr_name = unknown_mgr.group(1)
            manager_changes.append(
                ManagerChange(
                    subject_name="Ledger team",
                    to_manager=mgr_name,
                    subject_is_team=True,
                )
            )
            ambiguities.append(
                Ambiguity(
                    field="manager",
                    description=f"Source references manager '{mgr_name}' described as unknown.",
                    severity=ValidationSeverity.ERROR,
                )
            )

        ledger = re.search(r"move the ([A-Za-z]+ team)", text, re.IGNORECASE)
        if ledger and "ledger" in ledger.group(1).lower():
            org_changes.append(
                OrgChange(
                    team_name="Ledger",
                    to_org_or_manager=unknown_mgr.group(1) if unknown_mgr else None,
                )
            )
            ambiguities.append(
                Ambiguity(
                    field="team",
                    description="Ledger team referenced but may not exist in directory.",
                    severity=ValidationSeverity.ERROR,
                )
            )

        # Claimed approvals — NEVER mark independently_verified here
        if re.search(r"finance.*(approved|signed off|approval)", lower) or re.search(
            r"(approved|signed off).*finance", lower
        ):
            claim = re.search(
                r"([^.]*finance[^.]*?(?:approved|signed off|approval)[^.]*\.)",
                text,
                re.IGNORECASE,
            )
            claim_text = claim.group(1).strip() if claim else "Finance approval claimed in source"
            claimed.append(
                ClaimedApproval(
                    approver_role_or_name="Finance",
                    claim_text=claim_text,
                    independently_verified=False,
                    verification_note=(
                        "Claimed in source material only; not independently verified."
                    ),
                )
            )

        if not effective:
            ambiguities.append(
                Ambiguity(
                    field="effective_date",
                    description="Could not confidently parse an effective date.",
                    severity=ValidationSeverity.WARNING,
                )
            )

        confidence = 0.82 if org_changes and cost_center_changes else 0.55
        if ambiguities:
            confidence = min(confidence, 0.45)

        summary_parts = []
        if team_name:
            summary_parts.append(f"Move {team_name}")
        if cost_center_changes:
            cc = cost_center_changes[0]
            summary_parts.append(f"CC {cc.from_cost_center}→{cc.to_cost_center}")
        if exceptions:
            summary_parts.append(f"{len(exceptions)} exception(s)")

        return ExtractedRequest(
            effective_date=effective,
            summary="; ".join(summary_parts) or "Parsed freeform reorg request",
            people=people,
            org_changes=org_changes,
            manager_changes=manager_changes,
            cost_center_changes=cost_center_changes,
            exceptions=exceptions,
            claimed_approvals=claimed,
            ambiguities=ambiguities,
            assumptions=assumptions,
            confidence=confidence,
        )


class OpenAIProvider(LLMProvider):
    """
    Live LLM structured extraction via an OpenAI-compatible API.

    Uses LLM_API_KEY (required). Optional LLM_MODEL and LLM_BASE_URL from env
    (or Streamlit Cloud secrets mapped to env). This is only for the app's
    interpretation step (freeform text → typed ExtractedRequest), not for
    approvals or system writes.
    """

    name = "llm"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        from openai import OpenAI

        cfg = resolve_llm_settings()
        key = api_key or cfg["api_key"]
        self.model = model or cfg["model"] or "gpt-4o-mini"
        resolved_base = base_url if base_url is not None else cfg["base_url"]
        self.client = (
            OpenAI(api_key=key, base_url=resolved_base)
            if resolved_base
            else OpenAI(api_key=key)
        )

    def extract(self, raw_text: str) -> ExtractedRequest:
        safe_text = redact_for_prompt(raw_text)
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract structured reorganization requests from freeform "
                        "enterprise text. You never grant approvals. "
                        + EXTRACTION_SCHEMA_HINT
                    ),
                },
                {"role": "user", "content": safe_text},
            ],
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        # Force claimed approvals unverified at parse boundary
        for claim in data.get("claimed_approvals", []) or []:
            claim["independently_verified"] = False
            claim.setdefault(
                "verification_note",
                "Claimed in source material only; not independently verified.",
            )
        return ExtractedRequest.model_validate(data)


def resolve_llm_settings() -> dict[str, str | None]:
    """Read LLM config from environment only (no in-app key UI)."""
    return {
        "api_key": (os.getenv("LLM_API_KEY") or None),
        "model": (os.getenv("LLM_MODEL") or None),
        "base_url": (os.getenv("LLM_BASE_URL") or None),
    }


def llm_mode_label() -> str:
    """Human-readable interpretation mode for the UI."""
    if resolve_llm_settings()["api_key"]:
        return "Live LLM"
    return "Built-in demo parser"


def get_llm_provider() -> LLMProvider:
    """
    Use a live LLM when LLM_API_KEY is set in the environment.

    Otherwise fall back to the deterministic demo extractor so the walkthrough
    runs with no credentials. The LLM is only used to interpret freeform intake;
    it never authorizes or executes changes.
    """
    cfg = resolve_llm_settings()
    if cfg["api_key"]:
        try:
            return OpenAIProvider(
                api_key=cfg["api_key"],
                model=cfg["model"],
                base_url=cfg["base_url"],
            )
        except Exception:
            return DeterministicExtractor()
    return DeterministicExtractor()



def _parse_date(text: str) -> Optional[str]:
    patterns = [
        r"Effective\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"Effective\s+(\d{4}-\d{2}-\d{2})",
        r"Effective\s+([A-Za-z]+\s+\d{1,2})",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if not m:
            continue
        raw = m.group(1)
        for fmt in ("%B %d, %Y", "%Y-%m-%d", "%B %d"):
            try:
                dt = datetime.strptime(raw, fmt)
                if fmt == "%B %d":
                    dt = dt.replace(year=datetime.now().year)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
    return None


def _parse_headcount(text: str) -> Optional[int]:
    m = re.search(r"\b(\d+)\s+(?:team members|engineers|people|employees)\b", text, re.I)
    if m:
        return int(m.group(1))
    return None


def _find_names(text: str) -> list[str]:
    # Simple Proper Name extractor excluding month names
    months = {
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
        "effective",
        "finance",
        "platform",
        "payments",
        "engineering",
        "ledger",
    }
    found = re.findall(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", text)
    out: list[str] = []
    for name in found:
        if name.split()[0].lower() in months:
            continue
        if name not in out:
            out.append(name)
    return out
