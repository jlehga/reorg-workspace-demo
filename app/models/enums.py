"""Shared enumerations for the Reorg Case domain."""

from enum import Enum


class CaseStatus(str, Enum):
    DRAFT = "draft"
    INTERPRETED = "interpreted"
    VALIDATED = "validated"
    NEEDS_REVIEW = "needs_review"
    PLANNED = "planned"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    NEEDS_HUMAN_ACTION = "needs_human_action"
    RECONCILING = "reconciling"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class SourceType(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    DOCUMENT = "document"
    FREEFORM = "freeform"


class ActionStatus(str, Enum):
    PENDING = "pending"
    BLOCKED = "blocked"
    RUNNING = "running"
    NEEDS_HUMAN_ACTION = "needs_human_action"
    COMPLETE = "complete"
    FAILED = "failed"
    SKIPPED = "skipped"


class IntegrationType(str, Enum):
    AUTOMATED = "automated"
    MANUAL = "manual"
    APPROVAL_GATE = "approval_gate"


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CONFLICT = "conflict"


class ReconciliationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    PENDING = "pending"
    SKIPPED = "skipped"


class ActorType(str, Enum):
    SYSTEM = "system"
    LLM = "llm"
    HUMAN = "human"
    POLICY = "policy"
    INTEGRATION = "integration"


class AuditEventType(str, Enum):
    CASE_CREATED = "CASE_CREATED"
    REQUEST_INTERPRETED = "REQUEST_INTERPRETED"
    ENTITY_VALIDATED = "ENTITY_VALIDATED"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    PLAN_GENERATED = "PLAN_GENERATED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    ACTION_STARTED = "ACTION_STARTED"
    ACTION_COMPLETED = "ACTION_COMPLETED"
    ACTION_FAILED = "ACTION_FAILED"
    HUMAN_TASK_CREATED = "HUMAN_TASK_CREATED"
    HUMAN_TASK_COMPLETED = "HUMAN_TASK_COMPLETED"
    RECONCILIATION_STARTED = "RECONCILIATION_STARTED"
    RECONCILIATION_FAILED = "RECONCILIATION_FAILED"
    RECONCILIATION_PASSED = "RECONCILIATION_PASSED"
    CASE_COMPLETED = "CASE_COMPLETED"
    CASE_BLOCKED = "CASE_BLOCKED"
