"""Execution plan, actions, human tasks, and reconciliation models."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.enums import ActionStatus, IntegrationType, ReconciliationStatus


class PlannedAction(BaseModel):
    id: str
    name: str
    system: str
    description: str
    integration_type: IntegrationType
    depends_on: list[str] = Field(default_factory=list)
    status: ActionStatus = ActionStatus.PENDING
    payload: dict[str, Any] = Field(default_factory=dict)
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    expected_state: dict[str, Any] = Field(default_factory=dict)


class HumanTask(BaseModel):
    id: str
    action_id: str
    assigned_role: str
    title: str
    instructions: str
    required_fields: dict[str, str] = Field(default_factory=dict)
    expected_state: dict[str, Any] = Field(default_factory=dict)
    completion_evidence: Optional[dict[str, Any]] = None
    status: ActionStatus = ActionStatus.NEEDS_HUMAN_ACTION
    entered_values: dict[str, str] = Field(default_factory=dict)


class ApprovalRequirement(BaseModel):
    id: str
    role: str
    reason: str
    required: bool = True
    granted: bool = False
    granted_by: Optional[str] = None
    granted_at: Optional[str] = None


class ChangePlan(BaseModel):
    ordered_actions: list[PlannedAction] = Field(default_factory=list)
    approval_requirements: list[ApprovalRequirement] = Field(default_factory=list)
    blast_radius_summary: str = ""
    unresolved_risks: list[str] = Field(default_factory=list)


class ReconciliationCheck(BaseModel):
    system: str
    field: str
    expected: str
    observed: str
    status: ReconciliationStatus
    notes: Optional[str] = None


class ReconciliationResult(BaseModel):
    checks: list[ReconciliationCheck] = Field(default_factory=list)
    overall_status: ReconciliationStatus = ReconciliationStatus.PENDING
    summary: str = ""
    blocked_systems: list[str] = Field(default_factory=list)
