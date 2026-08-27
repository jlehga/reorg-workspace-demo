"""Reconciliation — expected vs observed authoritative state."""

from __future__ import annotations

from app.data.store import EnterpriseStore
from app.integrations.adapters import build_adapters
from app.models.case import ReorgCase
from app.models.enums import (
    ActorType,
    AuditEventType,
    CaseStatus,
    ReconciliationStatus,
)
from app.models.plan import ReconciliationCheck, ReconciliationResult
from app.utils.audit import append_audit


class ReconciliationService:
    def __init__(self, store: EnterpriseStore) -> None:
        self.store = store
        self.adapters = build_adapters(store)

    def reconcile(self, case: ReorgCase) -> ReconciliationResult:
        assert case.change_plan is not None
        append_audit(
            case,
            AuditEventType.RECONCILIATION_STARTED,
            "Comparing expected plan state to observed systems of record.",
        )

        actions_by_id = {a.id: a for a in case.change_plan.ordered_actions}
        team_id = actions_by_id["update_hris"].payload.get("team_id")
        expected_leader = actions_by_id["update_hris"].expected_state.get("org_leader", "")
        expected_cc = actions_by_id["update_headcount"].expected_state.get(
            "cost_center", ""
        )

        checks: list[ReconciliationCheck] = []

        hris = self.adapters["HRIS"].observe(team_id)
        checks.append(
            ReconciliationCheck(
                system="HRIS",
                field="org_leader",
                expected=str(expected_leader),
                observed=str(hris.get("org_leader", "")),
                status=(
                    ReconciliationStatus.PASSED
                    if hris.get("org_leader") == expected_leader
                    else ReconciliationStatus.FAILED
                ),
            )
        )

        hc = self.adapters["Headcount Planning"].observe(team_id)
        checks.append(
            ReconciliationCheck(
                system="Headcount",
                field="cost_center",
                expected=str(expected_cc),
                observed=str(hc.get("cost_center", "")),
                status=(
                    ReconciliationStatus.PASSED
                    if hc.get("cost_center") == expected_cc
                    else ReconciliationStatus.FAILED
                ),
            )
        )

        ca = self.adapters["Cost Allocation"].observe(team_id)
        checks.append(
            ReconciliationCheck(
                system="Cost Allocation",
                field="cost_center",
                expected=str(expected_cc),
                observed=str(ca.get("cost_center", "")),
                status=(
                    ReconciliationStatus.PASSED
                    if ca.get("cost_center") == expected_cc
                    else ReconciliationStatus.FAILED
                ),
            )
        )

        gl = self.adapters["GL Mapping"].observe(team_id)
        gl_ok = gl.get("cost_center") == expected_cc
        checks.append(
            ReconciliationCheck(
                system="GL Mapping",
                field="cost_center",
                expected=str(expected_cc),
                observed=str(gl.get("cost_center", "")),
                status=(
                    ReconciliationStatus.PASSED
                    if gl_ok
                    else ReconciliationStatus.FAILED
                ),
                notes=None
                if gl_ok
                else "Manual GL entry does not match approved plan.",
            )
        )

        reporting = self.adapters["Reporting"].observe(team_id)
        if not gl_ok:
            # Block reporting propagation when GL is wrong
            reporting_adapter = self.adapters["Reporting"]
            reporting_adapter.block(  # type: ignore[attr-defined]
                "Reorg incomplete. GL mapping does not match the approved plan. "
                "Reporting propagation has been blocked."
            )
            checks.append(
                ReconciliationCheck(
                    system="Reporting",
                    field="sync",
                    expected=str(expected_cc),
                    observed="n/a",
                    status=ReconciliationStatus.BLOCKED,
                    notes=self.store.reporting.get("block_reason"),
                )
            )
        else:
            checks.append(
                ReconciliationCheck(
                    system="Reporting",
                    field="synced_cost_center",
                    expected=str(expected_cc),
                    observed=str(reporting.get("synced_cost_center") or "n/a"),
                    status=(
                        ReconciliationStatus.PASSED
                        if reporting.get("synced_cost_center") == expected_cc
                        else ReconciliationStatus.FAILED
                    ),
                )
            )

        failed = [c for c in checks if c.status == ReconciliationStatus.FAILED]
        blocked = [c for c in checks if c.status == ReconciliationStatus.BLOCKED]

        if failed or blocked:
            overall = (
                ReconciliationStatus.FAILED if failed else ReconciliationStatus.BLOCKED
            )
            summary = (
                "Reorg incomplete. "
                + "; ".join(
                    (c.notes or f"{c.system} {c.field} mismatch")
                    for c in failed + blocked
                )
            )
            case.status = CaseStatus.FAILED if failed else CaseStatus.BLOCKED
            append_audit(
                case,
                AuditEventType.RECONCILIATION_FAILED,
                summary,
                status=overall.value,
            )
            if blocked:
                append_audit(
                    case,
                    AuditEventType.CASE_BLOCKED,
                    summary,
                    status="blocked",
                )
        else:
            overall = ReconciliationStatus.PASSED
            summary = "All systems reconciled. Reorg case complete."
            case.status = CaseStatus.COMPLETED
            case.final_summary = summary
            append_audit(
                case,
                AuditEventType.RECONCILIATION_PASSED,
                summary,
                status="passed",
            )
            append_audit(
                case,
                AuditEventType.CASE_COMPLETED,
                summary,
                actor_type=ActorType.SYSTEM,
                status="completed",
            )

        result = ReconciliationResult(
            checks=checks,
            overall_status=overall,
            summary=summary,
            blocked_systems=[c.system for c in blocked],
        )
        case.reconciliation = result
        return result
