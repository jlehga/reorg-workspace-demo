"""Tests encoding core design intent — not coverage theater."""

from __future__ import annotations

import pytest

from app.agents.llm import DeterministicExtractor
from app.data.scenarios import SCENARIO_A_SUCCESS, SCENARIO_B_FAILURE
from app.models.enums import ActionStatus, CaseStatus, ReconciliationStatus
from app.models.extraction import ClaimedApproval, ExtractedRequest
from app.workflow.engine import ReorgWorkflow


@pytest.fixture
def wf() -> ReorgWorkflow:
    return ReorgWorkflow(llm=DeterministicExtractor())


def test_structured_extraction_schema_validation(wf: ReorgWorkflow) -> None:
    """LLM/extractor output must conform to typed ExtractedRequest."""
    case = wf.create_case(SCENARIO_A_SUCCESS)
    extracted = wf.interpreter.interpret(case)
    assert isinstance(extracted, ExtractedRequest)
    assert extracted.effective_date == "2026-09-01"
    assert any("Payments" in o.team_name for o in extracted.org_changes)
    assert any(c.to_cost_center == "CC-4175" for c in extracted.cost_center_changes)
    assert any(e.person_name == "Sarah Patel" for e in extracted.exceptions)
    # Round-trip through schema
    ExtractedRequest.model_validate(extracted.model_dump())


def test_claimed_approval_is_not_verified_authorization(wf: ReorgWorkflow) -> None:
    """
    'Finance has approved' in freeform text must NOT become verified approval.
    """
    case = wf.analyze(wf.create_case(SCENARIO_A_SUCCESS))
    assert case.extracted_request is not None
    assert case.validation is not None

    claims = case.extracted_request.claimed_approvals
    assert claims, "Expected a Finance approval claim to be extracted"
    assert all(isinstance(c, ClaimedApproval) for c in claims)
    assert all(c.independently_verified is False for c in claims)

    verified = case.validation.claimed_vs_verified_approvals
    assert verified
    assert all(v.independently_verified is False for v in verified)
    assert any(
        "could not be independently verified" in (v.verification_note or "").lower()
        for v in verified
    )
    # Policy still requires explicit Finance approval gate
    assert case.change_plan is not None
    assert any(a.role == "Finance" for a in case.change_plan.approval_requirements)


def test_dependency_blocking_when_prerequisite_fails(wf: ReorgWorkflow) -> None:
    """Downstream actions must not execute when a dependency failed."""
    case = wf.analyze(wf.create_case(SCENARIO_A_SUCCESS))
    wf.approve(case, granted_by="tester@example.com")

    # Force HRIS action to fail before running
    hris = next(a for a in case.change_plan.ordered_actions if a.id == "update_hris")
    hris.status = ActionStatus.FAILED
    hris.error = "simulated failure"

    # Mark prior deps complete so only HRIS failure matters
    for a in case.change_plan.ordered_actions:
        if a.id in ("verify_preconditions", "human_approval_gate"):
            a.status = ActionStatus.COMPLETE

    wf.engine._block_dependents(case, "update_hris")  # noqa: SLF001 — intentional

    headcount = next(a for a in case.change_plan.ordered_actions if a.id == "update_headcount")
    cost = next(a for a in case.change_plan.ordered_actions if a.id == "update_cost_allocation")
    gl = next(a for a in case.change_plan.ordered_actions if a.id == "update_gl_mapping")
    reporting = next(a for a in case.change_plan.ordered_actions if a.id == "update_reporting")

    assert headcount.status == ActionStatus.BLOCKED
    assert cost.status == ActionStatus.BLOCKED
    assert gl.status == ActionStatus.BLOCKED
    assert reporting.status == ActionStatus.BLOCKED


def test_incorrect_gl_prevents_case_completion(wf: ReorgWorkflow) -> None:
    """Reconciliation failure (wrong GL) must prevent case completion."""
    case = wf.analyze(wf.create_case(SCENARIO_A_SUCCESS))
    wf.approve(case, granted_by="tester@example.com")
    case = wf.execute(case)
    assert case.status == CaseStatus.NEEDS_HUMAN_ACTION
    assert case.human_tasks

    case = wf.complete_manual_gl(
        case,
        entered_cost_center="CC-4175",
        simulate_incorrect_entry=True,
    )

    assert case.reconciliation is not None
    assert case.reconciliation.overall_status in (
        ReconciliationStatus.FAILED,
        ReconciliationStatus.BLOCKED,
    )
    assert case.status in (CaseStatus.FAILED, CaseStatus.BLOCKED)
    assert case.status != CaseStatus.COMPLETED

    gl_check = next(c for c in case.reconciliation.checks if c.system == "GL Mapping")
    assert gl_check.status == ReconciliationStatus.FAILED
    reporting = next(c for c in case.reconciliation.checks if c.system == "Reporting")
    assert reporting.status == ReconciliationStatus.BLOCKED


def test_manual_task_still_requires_reconciliation(wf: ReorgWorkflow) -> None:
    """Marking a manual task complete is not sufficient — reconcile expected vs observed."""
    case = wf.analyze(wf.create_case(SCENARIO_A_SUCCESS))
    wf.approve(case, granted_by="tester@example.com")
    case = wf.execute(case)

    task = case.human_tasks[-1]
    assert task.assigned_role == "Finance Operations"
    assert "no API" in task.instructions.lower() or "Manual" in task.instructions

    case = wf.complete_manual_gl(case, entered_cost_center="CC-4175")
    assert case.reconciliation is not None
    assert case.reconciliation.overall_status == ReconciliationStatus.PASSED
    assert case.status == CaseStatus.COMPLETED

    # Happy path observed states
    by_system = {c.system: c for c in case.reconciliation.checks}
    assert by_system["HRIS"].status == ReconciliationStatus.PASSED
    assert by_system["GL Mapping"].observed == "CC-4175"


def test_scenario_b_surfaces_conflicts(wf: ReorgWorkflow) -> None:
    """Failure scenario: inactive CC, headcount mismatch, unknown entities."""
    case = wf.analyze(wf.create_case(SCENARIO_B_FAILURE))
    assert case.validation is not None
    codes = {c.code for c in case.validation.conflicts}
    assert "HEADCOUNT_MISMATCH" in codes or "COST_CENTER_INACTIVE" in codes
    assert case.validation.is_safe_to_plan is False
    # Claimed finance approval still unverified
    assert any(
        not c.independently_verified
        for c in case.validation.claimed_vs_verified_approvals
    )
