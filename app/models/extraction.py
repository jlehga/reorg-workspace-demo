"""Typed models for LLM extraction output and validation results."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import ValidationSeverity


class PersonRef(BaseModel):
    name: str
    employee_id: Optional[str] = None
    role_hint: Optional[str] = None


class OrgChange(BaseModel):
    team_name: str
    from_org_or_manager: Optional[str] = None
    to_org_or_manager: Optional[str] = None
    expected_headcount: Optional[int] = None


class ManagerChange(BaseModel):
    subject_name: str
    from_manager: Optional[str] = None
    to_manager: Optional[str] = None
    subject_is_team: bool = False


class CostCenterChange(BaseModel):
    subject_name: str
    from_cost_center: Optional[str] = None
    to_cost_center: Optional[str] = None
    subject_type: str = "team"  # team | employee


class ExceptionMove(BaseModel):
    """Individual who should not follow the default team move."""

    person_name: str
    to_org_or_manager: Optional[str] = None
    to_manager: Optional[str] = None
    to_cost_center: Optional[str] = None
    notes: Optional[str] = None


class ClaimedApproval(BaseModel):
    """Approval mentioned in source text — NOT authoritative authorization."""

    approver_role_or_name: str
    claim_text: str
    independently_verified: bool = False
    verification_note: Optional[str] = None


class Ambiguity(BaseModel):
    field: str
    description: str
    severity: ValidationSeverity = ValidationSeverity.WARNING


class ExtractedRequest(BaseModel):
    """Structured interpretation produced by the LLM (proposed, not truth)."""

    effective_date: Optional[str] = None
    summary: Optional[str] = None
    people: list[PersonRef] = Field(default_factory=list)
    org_changes: list[OrgChange] = Field(default_factory=list)
    manager_changes: list[ManagerChange] = Field(default_factory=list)
    cost_center_changes: list[CostCenterChange] = Field(default_factory=list)
    exceptions: list[ExceptionMove] = Field(default_factory=list)
    claimed_approvals: list[ClaimedApproval] = Field(default_factory=list)
    ambiguities: list[Ambiguity] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class VerifiedEntity(BaseModel):
    entity_type: str
    name: str
    entity_id: Optional[str] = None
    found: bool
    details: dict = Field(default_factory=dict)


class ValidationIssue(BaseModel):
    code: str
    message: str
    severity: ValidationSeverity
    related_entity: Optional[str] = None
    source_claim: Optional[str] = None
    authoritative_finding: Optional[str] = None


class ValidationResult(BaseModel):
    verified_entities: list[VerifiedEntity] = Field(default_factory=list)
    issues: list[ValidationIssue] = Field(default_factory=list)
    conflicts: list[ValidationIssue] = Field(default_factory=list)
    ambiguities: list[Ambiguity] = Field(default_factory=list)
    claimed_vs_verified_approvals: list[ClaimedApproval] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    is_safe_to_plan: bool = False
    people_impacted_count: int = 0
