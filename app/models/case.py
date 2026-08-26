"""Canonical Reorg Case — system of record for reorg execution."""

from __future__ import annotations

from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.audit import AuditEvent, utc_now_iso
from app.models.enums import CaseStatus, SourceType
from app.models.extraction import ExtractedRequest, ValidationResult
from app.models.plan import ChangePlan, HumanTask, ReconciliationResult


class SourceMaterial(BaseModel):
    raw_text: str
    source_type: SourceType = SourceType.FREEFORM
    received_at: str = Field(default_factory=utc_now_iso)


class ReorgCase(BaseModel):
    """
    System of record for reorg *execution*.

    Domain systems (HRIS, Finance, Planning) remain authoritative for their
    underlying data. This object answers: what was requested, interpreted,
    validated, approved, executed, and reconciled.
    """

    id: str = Field(default_factory=lambda: f"RC-{uuid4().hex[:8].upper()}")
    status: CaseStatus = CaseStatus.DRAFT
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)

    source: SourceMaterial
    extracted_request: Optional[ExtractedRequest] = None
    validation: Optional[ValidationResult] = None
    change_plan: Optional[ChangePlan] = None
    human_tasks: list[HumanTask] = Field(default_factory=list)
    reconciliation: Optional[ReconciliationResult] = None
    audit_log: list[AuditEvent] = Field(default_factory=list)

    extractor_provider: Optional[str] = None
    final_summary: Optional[str] = None

    def touch(self) -> None:
        self.updated_at = utc_now_iso()
