"""Audit trail models — no raw sensitive values."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.enums import ActorType, AuditEventType


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=utc_now_iso)
    event_type: AuditEventType
    actor_type: ActorType
    actor_id: str = "system"
    object_id: Optional[str] = None
    action_id: Optional[str] = None
    status: Optional[str] = None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
