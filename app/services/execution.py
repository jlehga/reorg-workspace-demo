"""Governed execution engine with dependency blocking and manual tasks."""

from __future__ import annotations

from typing import Optional

from app.data.store import EnterpriseStore
from app.integrations.adapters import GLMappingAdapter, build_adapters
from app.models.case import ReorgCase
from app.models.enums import (
    ActionStatus,
    ActorType,
    AuditEventType,
    CaseStatus,
    IntegrationType,
)
from app.models.plan import HumanTask, PlannedAction
from app.policies.approval import ApprovalPolicy
from app.services.reconciliation import ReconciliationService
from app.utils.audit import append_audit


class ExecutionEngine:
    def __init__(
        self,
        store: EnterpriseStore,
        policy: ApprovalPolicy | None = None,
    ) -> None:
        self.store = store
        self.policy = policy or ApprovalPolicy()
        self.adapters = build_adapters(store)
        self.reconciliation = ReconciliationService(store)

    def _deps_satisfied(self, case: ReorgCase, action: PlannedAction) -> bool:
        assert case.change_plan is not None
        by_id = {a.id: a for a in case.change_plan.ordered_actions}
        for dep_id in action.depends_on:
            dep = by_id[dep_id]
            if dep.status != ActionStatus.COMPLETE:
                return False
        return True

    def _deps_failed(self, case: ReorgCase, action: PlannedAction) -> Optional[str]:
        assert case.change_plan is not None
        by_id = {a.id: a for a in case.change_plan.ordered_actions}
        for dep_id in action.depends_on:
            dep = by_id[dep_id]
            if dep.status in (ActionStatus.FAILED, ActionStatus.BLOCKED, ActionStatus.SKIPPED):
                return dep_id
            if dep.status == ActionStatus.NEEDS_HUMAN_ACTION:
                return dep_id
        return None

    def run_available(self, case: ReorgCase) -> ReorgCase:
        """Execute all currently runnable automated actions; pause on manual/approval."""
        assert case.change_plan is not None

        if not self.policy.all_granted(case):
            case.status = CaseStatus.AWAITING_APPROVAL
            return case

        case.status = CaseStatus.EXECUTING
        progress = True
        while progress:
            progress = False
            for action in case.change_plan.ordered_actions:
                if action.status != ActionStatus.PENDING:
                    continue

                failed_dep = self._deps_failed(case, action)
                if failed_dep:
                    action.status = ActionStatus.BLOCKED
                    action.error = f"Blocked because dependency '{failed_dep}' is not complete."
                    append_audit(
                        case,
                        AuditEventType.ACTION_FAILED,
                        action.error,
                        action_id=action.id,
                        status="blocked",
                    )
                    progress = True
                    continue

                if not self._deps_satisfied(case, action):
                    continue

                if action.integration_type == IntegrationType.APPROVAL_GATE:
                    action.status = ActionStatus.RUNNING
                    append_audit(
                        case,
                        AuditEventType.ACTION_STARTED,
                        f"Evaluating approval gate '{action.id}'.",
                        action_id=action.id,
                    )
                    if self.policy.all_granted(case):
                        action.status = ActionStatus.COMPLETE
                        action.result = {"approvals": "granted"}
                        append_audit(
                            case,
                            AuditEventType.ACTION_COMPLETED,
                            "Approval gate passed.",
                            action_id=action.id,
                            status="complete",
                        )
                        progress = True
                    else:
                        action.status = ActionStatus.BLOCKED
                        action.error = "Required approvals not granted."
                    continue

                if action.integration_type == IntegrationType.MANUAL:
                    self._create_human_task(case, action)
                    case.status = CaseStatus.NEEDS_HUMAN_ACTION
                    return case

                if action.id == "reconcile":
                    action.status = ActionStatus.RUNNING
                    append_audit(
                        case,
                        AuditEventType.ACTION_STARTED,
                        "Starting reconciliation.",
                        action_id=action.id,
                    )
                    case.status = CaseStatus.RECONCILING
                    result = self.reconciliation.reconcile(case)
                    if result.overall_status.value == "passed":
                        action.status = ActionStatus.COMPLETE
                        action.result = {"summary": result.summary}
                        append_audit(
                            case,
                            AuditEventType.ACTION_COMPLETED,
                            "Reconciliation passed.",
                            action_id=action.id,
                            status="complete",
                        )
                    else:
                        action.status = ActionStatus.FAILED
                        action.error = result.summary
                        append_audit(
                            case,
                            AuditEventType.ACTION_FAILED,
                            result.summary,
                            action_id=action.id,
                            status="failed",
                        )
                    return case

                # Automated adapter
                progress = True
                self._run_automated(case, action)
                if action.status == ActionStatus.FAILED:
                    self._block_dependents(case, action.id)
                    case.status = CaseStatus.FAILED
                    return case

        # If manual tasks outstanding
        if any(
            a.status == ActionStatus.NEEDS_HUMAN_ACTION
            for a in case.change_plan.ordered_actions
        ):
            case.status = CaseStatus.NEEDS_HUMAN_ACTION
        elif all(
            a.status == ActionStatus.COMPLETE for a in case.change_plan.ordered_actions
        ):
            if case.status != CaseStatus.COMPLETED:
                case.status = CaseStatus.COMPLETED
        return case

    def _run_automated(self, case: ReorgCase, action: PlannedAction) -> None:
        action.status = ActionStatus.RUNNING
        append_audit(
            case,
            AuditEventType.ACTION_STARTED,
            f"Starting {action.system} action '{action.name}'.",
            action_id=action.id,
            actor_type=ActorType.INTEGRATION,
            actor_id=action.system,
        )
        adapter = self.adapters.get(action.system)
        if adapter is None:
            action.status = ActionStatus.FAILED
            action.error = f"No adapter for system {action.system}"
            append_audit(
                case,
                AuditEventType.ACTION_FAILED,
                action.error,
                action_id=action.id,
                status="failed",
            )
            return
        try:
            result = adapter.execute(action)
            action.result = result
            action.status = ActionStatus.COMPLETE
            append_audit(
                case,
                AuditEventType.ACTION_COMPLETED,
                f"Completed {action.system} action '{action.name}'.",
                action_id=action.id,
                actor_type=ActorType.INTEGRATION,
                actor_id=action.system,
                status="complete",
                metadata={"result_keys": list(result.keys())},
            )
        except Exception as exc:  # noqa: BLE001 — surface adapter failures in case
            action.status = ActionStatus.FAILED
            action.error = str(exc)
            append_audit(
                case,
                AuditEventType.ACTION_FAILED,
                f"{action.system} failed: {exc}",
                action_id=action.id,
                status="failed",
            )

    def _block_dependents(self, case: ReorgCase, failed_id: str) -> None:
        assert case.change_plan is not None
        changed = True
        while changed:
            changed = False
            for action in case.change_plan.ordered_actions:
                if action.status != ActionStatus.PENDING:
                    continue
                if failed_id in action.depends_on or self._deps_failed(case, action):
                    action.status = ActionStatus.BLOCKED
                    action.error = (
                        f"Blocked because dependency '{failed_id}' failed or is incomplete."
                    )
                    changed = True

    def _create_human_task(self, case: ReorgCase, action: PlannedAction) -> HumanTask:
        action.status = ActionStatus.NEEDS_HUMAN_ACTION
        payload = action.payload
        task = HumanTask(
            id=f"HT-{action.id}",
            action_id=action.id,
            assigned_role=payload.get("assigned_role", "Finance Operations"),
            title=f"Key GL mapping change for {payload.get('team_name')}",
            instructions=(
                f"Integration type: Manual (no API)\n"
                f"Status: Action Required\n\n"
                f"Enter in the GL system:\n"
                f"  Team: {payload.get('team_name')}\n"
                f"  Old cost center: {payload.get('old_cost_center')}\n"
                f"  New cost center: {payload.get('new_cost_center')}\n"
                f"  Effective date: {payload.get('effective_date')}\n\n"
                f"Mark complete only after the GL entry is made. "
                f"The workflow will reconcile observed GL state against the approved plan."
            ),
            required_fields={
                "team": str(payload.get("team_name")),
                "old_cost_center": str(payload.get("old_cost_center")),
                "new_cost_center": str(payload.get("new_cost_center")),
                "effective_date": str(payload.get("effective_date")),
            },
            expected_state={"cost_center": payload.get("new_cost_center")},
            status=ActionStatus.NEEDS_HUMAN_ACTION,
        )
        # Replace if recreated
        case.human_tasks = [t for t in case.human_tasks if t.action_id != action.id]
        case.human_tasks.append(task)
        append_audit(
            case,
            AuditEventType.HUMAN_TASK_CREATED,
            f"Created manual task for {action.system} assigned to {task.assigned_role}.",
            actor_type=ActorType.SYSTEM,
            action_id=action.id,
            metadata={"task_id": task.id, "role": task.assigned_role},
        )
        return task

    def complete_human_task(
        self,
        case: ReorgCase,
        task_id: str,
        *,
        entered_cost_center: str,
        completed_by: str = "finance.ops@example.com",
        simulate_incorrect_entry: bool = False,
    ) -> ReorgCase:
        assert case.change_plan is not None
        task = next((t for t in case.human_tasks if t.id == task_id), None)
        if not task:
            raise ValueError(f"Unknown task {task_id}")

        action = next(a for a in case.change_plan.ordered_actions if a.id == task.action_id)
        gl_adapter: GLMappingAdapter = self.adapters["GL Mapping"]  # type: ignore[assignment]

        expected_cc = str(task.expected_state.get("cost_center") or "")
        # If simulate_incorrect_entry, write wrong CC to demonstrate reconciliation failure
        if simulate_incorrect_entry:
            wrong = action.payload.get("old_cost_center") or "CC-4102"
            result = gl_adapter.apply_human_entry(
                action.payload["team_id"],
                expected_cc,
                force_incorrect=True,
                incorrect_value=str(wrong),
            )
            entered = str(wrong)
        else:
            result = gl_adapter.apply_human_entry(
                action.payload["team_id"],
                entered_cost_center,
            )
            entered = entered_cost_center

        task.entered_values = {
            "new_cost_center": entered,
            "completed_by": completed_by,
        }
        task.completion_evidence = {
            "entered_cost_center": entered,
            "gl_snapshot": result,
        }
        task.status = ActionStatus.COMPLETE
        action.status = ActionStatus.COMPLETE
        action.result = result

        append_audit(
            case,
            AuditEventType.HUMAN_TASK_COMPLETED,
            f"Manual GL task marked complete by {completed_by} (entered={entered}).",
            actor_type=ActorType.HUMAN,
            actor_id=completed_by,
            action_id=action.id,
            metadata={
                "task_id": task.id,
                "entered_cost_center": entered,
                # do not log unrelated PII
            },
        )
        append_audit(
            case,
            AuditEventType.ACTION_COMPLETED,
            "GL mapping manual action recorded; reconciliation still required.",
            action_id=action.id,
            status="complete",
        )

        # Continue downstream (reporting + reconcile)
        return self.run_available(case)
