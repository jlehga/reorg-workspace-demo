"""Dependency-aware execution plan generation."""

from __future__ import annotations

from app.data.store import EnterpriseStore
from app.models.case import ReorgCase
from app.models.enums import (
    ActorType,
    AuditEventType,
    CaseStatus,
    IntegrationType,
)
from app.models.plan import ChangePlan, PlannedAction
from app.policies.approval import ApprovalPolicy
from app.utils.audit import append_audit


class PlanningService:
    """
    Builds an explicit dependency graph of actions.

    Order (conceptual):
      validate_org → human_approval → hris_update → (headcount || cost_alloc)
      → gl_mapping (manual) → reporting → reconcile
    """

    def __init__(self, store: EnterpriseStore, policy: ApprovalPolicy | None = None) -> None:
        self.store = store
        self.policy = policy or ApprovalPolicy()

    def build_plan(self, case: ReorgCase) -> ChangePlan:
        assert case.extracted_request is not None
        assert case.validation is not None
        req = case.extracted_request

        team = None
        for oc in req.org_changes:
            team = self.store.find_team_by_name(oc.team_name)
            if team:
                break

        to_manager_name = None
        from_manager_name = None
        if req.org_changes:
            to_manager_name = req.org_changes[0].to_org_or_manager
            from_manager_name = req.org_changes[0].from_org_or_manager

        to_mgr = (
            self.store.find_employee_by_name(to_manager_name)
            if to_manager_name
            else None
        )
        cc_from = None
        cc_to = None
        if req.cost_center_changes:
            cc_from = req.cost_center_changes[0].from_cost_center
            cc_to = req.cost_center_changes[0].to_cost_center

        exception_payload = [
            e.model_dump() for e in req.exceptions
        ]

        effective_date = req.effective_date or "unspecified"
        team_id = team["id"] if team else "UNKNOWN"
        team_name = team["name"] if team else (req.org_changes[0].team_name if req.org_changes else "Unknown")

        actions: list[PlannedAction] = [
            PlannedAction(
                id="verify_preconditions",
                name="Verify organization / manager preconditions",
                system="Directory",
                description="Confirm validated entities still match authoritative snapshot before writes.",
                integration_type=IntegrationType.AUTOMATED,
                depends_on=[],
                payload={"team_id": team_id},
                expected_state={"preconditions": "ok"},
            ),
            PlannedAction(
                id="human_approval_gate",
                name="Human approval gate",
                system="Policy",
                description="Deterministic policy gate — LLM cannot authorize execution.",
                integration_type=IntegrationType.APPROVAL_GATE,
                depends_on=["verify_preconditions"],
                payload={},
                expected_state={"approvals": "granted"},
            ),
            PlannedAction(
                id="update_hris",
                name="Update HRIS org / manager assignments",
                system="HRIS",
                description=(
                    f"Move {team_name} under {to_manager_name}; apply exception moves."
                ),
                integration_type=IntegrationType.AUTOMATED,
                depends_on=["human_approval_gate"],
                payload={
                    "team_id": team_id,
                    "to_manager_id": to_mgr["id"] if to_mgr else None,
                    "to_manager_name": to_manager_name,
                    "from_manager_name": from_manager_name,
                    "exceptions": exception_payload,
                    "effective_date": effective_date,
                },
                expected_state={
                    "org_leader": to_manager_name or "",
                    "team_id": team_id,
                },
            ),
            PlannedAction(
                id="update_headcount",
                name="Update headcount plan",
                system="Headcount Planning",
                description=f"Align headcount plan cost center to {cc_to} for {team_name}.",
                integration_type=IntegrationType.AUTOMATED,
                depends_on=["update_hris"],
                payload={
                    "team_id": team_id,
                    "cost_center": cc_to,
                    "effective_date": effective_date,
                },
                expected_state={"cost_center": cc_to or ""},
            ),
            PlannedAction(
                id="update_cost_allocation",
                name="Update cost allocation",
                system="Cost Allocation",
                description=f"Point cost allocation for {team_name} to {cc_to}.",
                integration_type=IntegrationType.AUTOMATED,
                depends_on=["update_hris"],
                payload={
                    "team_id": team_id,
                    "cost_center": cc_to,
                    "effective_date": effective_date,
                },
                expected_state={"cost_center": cc_to or ""},
            ),
            PlannedAction(
                id="update_gl_mapping",
                name="Update GL mapping (manual — no API)",
                system="GL Mapping",
                description=(
                    "Finance Operations must key the GL mapping change. "
                    "System orchestrates; human is the actuator."
                ),
                integration_type=IntegrationType.MANUAL,
                depends_on=["update_headcount", "update_cost_allocation"],
                payload={
                    "team_id": team_id,
                    "team_name": team_name,
                    "old_cost_center": cc_from,
                    "new_cost_center": cc_to,
                    "effective_date": effective_date,
                    "assigned_role": "Finance Operations",
                },
                expected_state={"cost_center": cc_to or ""},
            ),
            PlannedAction(
                id="update_reporting",
                name="Propagate to reporting",
                system="Reporting",
                description="Refresh reporting only after GL mapping reconciles.",
                integration_type=IntegrationType.AUTOMATED,
                depends_on=["update_gl_mapping"],
                payload={"team_id": team_id},
                expected_state={"synced": True},
            ),
            PlannedAction(
                id="reconcile",
                name="Reconcile expected vs observed state",
                system="Reconciliation",
                description="Completion requires observed state to match the approved plan.",
                integration_type=IntegrationType.AUTOMATED,
                depends_on=["update_reporting"],
                payload={"team_id": team_id},
                expected_state={},
            ),
        ]

        approvals = self.policy.evaluate(case)
        unresolved: list[str] = []
        for issue in case.validation.issues + case.validation.conflicts:
            unresolved.append(f"[{issue.severity.value}] {issue.message}")
        for amb in case.validation.ambiguities:
            unresolved.append(f"[ambiguity:{amb.field}] {amb.description}")
        for claim in case.validation.claimed_vs_verified_approvals:
            if not claim.independently_verified:
                unresolved.append(
                    claim.verification_note
                    or f"Unverified approval claim: {claim.approver_role_or_name}"
                )

        blast = (
            f"{case.validation.people_impacted_count} people on {team_name}; "
            f"cost center {cc_from} → {cc_to}; "
            f"{len(req.exceptions)} exception move(s); "
            f"GL mapping requires manual Finance Operations entry."
        )

        plan = ChangePlan(
            ordered_actions=actions,
            approval_requirements=approvals,
            blast_radius_summary=blast,
            unresolved_risks=unresolved,
        )
        case.change_plan = plan
        case.status = CaseStatus.AWAITING_APPROVAL
        append_audit(
            case,
            AuditEventType.PLAN_GENERATED,
            f"Generated dependency-aware plan with {len(actions)} actions.",
            actor_type=ActorType.SYSTEM,
            metadata={
                "action_ids": [a.id for a in actions],
                "approvals_required": [a.role for a in approvals],
            },
        )
        return plan
