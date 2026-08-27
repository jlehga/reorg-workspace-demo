"""Deterministic approval / policy gate — separate from LLM reasoning."""

from __future__ import annotations

from app.models.case import ReorgCase
from app.models.enums import ActorType, AuditEventType, CaseStatus
from app.models.plan import ApprovalRequirement
from app.utils.audit import append_audit


class ApprovalPolicy:
    """
    Policies authorize. The LLM may recommend a plan; it may not grant authority.

    Prototype rules intentionally simple and explainable.
    """

    BLAST_RADIUS_THRESHOLD = 10

    def evaluate(self, case: ReorgCase) -> list[ApprovalRequirement]:
        assert case.extracted_request is not None
        assert case.validation is not None

        reqs: list[ApprovalRequirement] = []
        reasons: list[str] = []

        # Always require HR Ops approval for org moves in this prototype
        reasons.append("Organization / manager changes modify HRIS records.")

        people = case.validation.people_impacted_count
        if people >= self.BLAST_RADIUS_THRESHOLD:
            reasons.append(
                f"Blast radius: {people} people impacted (threshold {self.BLAST_RADIUS_THRESHOLD})."
            )

        unverified = [
            c
            for c in case.validation.claimed_vs_verified_approvals
            if not c.independently_verified
        ]
        if unverified:
            reasons.append(
                "Source claims approval(s) that could not be independently verified."
            )

        if case.validation.conflicts:
            reasons.append("Validation conflicts exist and require human judgment.")

        if case.validation.ambiguities:
            reasons.append("Ambiguities remain in the interpreted request.")

        if case.validation.confidence < 0.7:
            reasons.append(
                f"Interpretation confidence is low ({case.validation.confidence:.2f})."
            )

        # Cost center / financial impact → Finance approval required
        if case.extracted_request.cost_center_changes:
            reqs.append(
                ApprovalRequirement(
                    id="apr-finance",
                    role="Finance",
                    reason=(
                        "Cost center changes affect budget, allocation, and GL mapping. "
                        + (
                            "Source claimed Finance approval but it was not independently verified."
                            if unverified
                            else "Explicit Finance authorization required before execution."
                        )
                    ),
                )
            )

        reqs.append(
            ApprovalRequirement(
                id="apr-hr-ops",
                role="HR Operations",
                reason=" ".join(reasons),
            )
        )

        for r in reqs:
            append_audit(
                case,
                AuditEventType.APPROVAL_REQUIRED,
                f"Approval required from {r.role}: {r.reason}",
                actor_type=ActorType.POLICY,
                actor_id="approval_policy",
                metadata={"approval_id": r.id, "role": r.role},
            )

        return reqs

    def grant(
        self,
        case: ReorgCase,
        *,
        granted_by: str,
        roles: list[str] | None = None,
    ) -> ReorgCase:
        assert case.change_plan is not None
        from app.models.audit import utc_now_iso

        target_roles = {r.lower() for r in (roles or [a.role for a in case.change_plan.approval_requirements])}
        for apr in case.change_plan.approval_requirements:
            if apr.role.lower() in target_roles:
                apr.granted = True
                apr.granted_by = granted_by
                apr.granted_at = utc_now_iso()
                append_audit(
                    case,
                    AuditEventType.APPROVAL_GRANTED,
                    f"{apr.role} approval granted by {granted_by}.",
                    actor_type=ActorType.HUMAN,
                    actor_id=granted_by,
                    metadata={"approval_id": apr.id},
                )

        if all(a.granted for a in case.change_plan.approval_requirements if a.required):
            case.status = CaseStatus.APPROVED
        return case

    def all_granted(self, case: ReorgCase) -> bool:
        if not case.change_plan:
            return False
        return all(
            a.granted for a in case.change_plan.approval_requirements if a.required
        )
