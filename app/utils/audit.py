"""Audit helpers attached to a Reorg Case."""

from __future__ import annotations

from typing import Any, Optional

from app.models.audit import AuditEvent
from app.models.case import ReorgCase
from app.models.enums import ActorType, AuditEventType


def append_audit(
    case: ReorgCase,
    event_type: AuditEventType,
    message: str,
    *,
    actor_type: ActorType = ActorType.SYSTEM,
    actor_id: str = "system",
    object_id: Optional[str] = None,
    action_id: Optional[str] = None,
    status: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> AuditEvent:
    event = AuditEvent(
        event_type=event_type,
        actor_type=actor_type,
        actor_id=actor_id,
        object_id=object_id or case.id,
        action_id=action_id,
        status=status,
        message=message,
        metadata=metadata or {},
    )
    case.audit_log.append(event)
    case.touch()
    return event
