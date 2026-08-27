"""Interpretation agent — LLM extraction + schema validation only."""

from __future__ import annotations

from app.agents.llm import LLMProvider, get_llm_provider
from app.models.case import ReorgCase
from app.models.enums import ActorType, AuditEventType, CaseStatus
from app.models.extraction import ExtractedRequest
from app.utils.audit import append_audit


class InterpretationAgent:
    """
    Agents interpret and plan. This agent only proposes structure.

    It must not mutate enterprise systems or grant approvals.
    """

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or get_llm_provider()

    def interpret(self, case: ReorgCase) -> ExtractedRequest:
        extracted = self.provider.extract(case.source.raw_text)
        # Schema already enforced by Pydantic; re-validate boundary
        extracted = ExtractedRequest.model_validate(extracted.model_dump())

        # Hard invariant: claimed approvals are never verified by the LLM path
        for claim in extracted.claimed_approvals:
            claim.independently_verified = False
            if not claim.verification_note:
                claim.verification_note = (
                    "Finance approval is referenced in the source material but "
                    "could not be independently verified."
                    if "finance" in claim.approver_role_or_name.lower()
                    else "Approval claim could not be independently verified."
                )

        case.extracted_request = extracted
        case.extractor_provider = self.provider.name
        case.status = CaseStatus.INTERPRETED
        append_audit(
            case,
            AuditEventType.REQUEST_INTERPRETED,
            f"Interpreted freeform request via provider '{self.provider.name}' "
            f"(confidence={extracted.confidence:.2f}).",
            actor_type=ActorType.LLM,
            actor_id=self.provider.name,
            status="ok",
            metadata={
                "confidence": extracted.confidence,
                "claimed_approvals": len(extracted.claimed_approvals),
                "ambiguities": len(extracted.ambiguities),
            },
        )
        return extracted
