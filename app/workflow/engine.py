"""Orchestration facade used by the UI and tests."""

from __future__ import annotations

from app.agents.extractor import InterpretationAgent
from app.agents.llm import LLMProvider
from app.data.store import EnterpriseStore, fresh_store
from app.models.case import ReorgCase, SourceMaterial
from app.models.enums import ActorType, AuditEventType, CaseStatus, SourceType
from app.policies.approval import ApprovalPolicy
from app.services.execution import ExecutionEngine
from app.services.planning import PlanningService
from app.services.validation import ValidationService
from app.utils.audit import append_audit


class ReorgWorkflow:
    """
    Capture → Interpret → Validate → Plan → Approve → Execute → Reconcile

    Thin facade so Streamlit stays free of business logic.
    """

    def __init__(
        self,
        store: EnterpriseStore | None = None,
        llm: LLMProvider | None = None,
    ) -> None:
        self.store = store or fresh_store()
        self.interpreter = InterpretationAgent(llm)
        self.validator = ValidationService(self.store)
        self.planner = PlanningService(self.store)
        self.policy = ApprovalPolicy()
        self.engine = ExecutionEngine(self.store, self.policy)

    def create_case(
        self, raw_text: str, source_type: SourceType = SourceType.FREEFORM
    ) -> ReorgCase:
        case = ReorgCase(
            source=SourceMaterial(raw_text=raw_text.strip(), source_type=source_type)
        )
        append_audit(
            case,
            AuditEventType.CASE_CREATED,
            "Reorg case created from freeform source material.",
            actor_type=ActorType.HUMAN,
            actor_id="submitter",
        )
        return case

    def analyze(self, case: ReorgCase) -> ReorgCase:
        """Slice A: interpret + validate + plan (plan may still need approval)."""
        self.interpreter.interpret(case)
        self.validator.validate(case)
        # Always generate a plan so the demo can show dependencies even when
        # conflicts exist — execution remains gated by policy + approval.
        self.planner.build_plan(case)
        if not case.validation or not case.validation.is_safe_to_plan:
            case.status = CaseStatus.NEEDS_REVIEW
        return case

    def approve(
        self,
        case: ReorgCase,
        *,
        granted_by: str = "demo.approver@example.com",
    ) -> ReorgCase:
        self.policy.grant(case, granted_by=granted_by)
        return case

    def execute(self, case: ReorgCase) -> ReorgCase:
        return self.engine.run_available(case)

    def complete_manual_gl(
        self,
        case: ReorgCase,
        *,
        entered_cost_center: str,
        simulate_incorrect_entry: bool = False,
        completed_by: str = "finance.ops@example.com",
    ) -> ReorgCase:
        if not case.human_tasks:
            raise RuntimeError("No human tasks pending")
        task = case.human_tasks[-1]
        return self.engine.complete_human_task(
            case,
            task.id,
            entered_cost_center=entered_cost_center,
            completed_by=completed_by,
            simulate_incorrect_entry=simulate_incorrect_entry,
        )
