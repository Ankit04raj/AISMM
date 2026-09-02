"""Production Audit Logger - Structured Compliance & Security Event Logging."""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, asdict


class AuditEventType(str, Enum):
    AUTH_LOGIN_SUCCESS = "AUTH_LOGIN_SUCCESS"
    AUTH_LOGIN_FAILED = "AUTH_LOGIN_FAILED"
    AUTH_TOKEN_REFRESH = "AUTH_TOKEN_REFRESH"
    AUTH_LOGOUT = "AUTH_LOGOUT"
    POST_CREATED = "POST_CREATED"
    POST_PUBLISHED = "POST_PUBLISHED"
    POST_DELETED = "POST_DELETED"
    PLATFORM_CONNECTED = "PLATFORM_CONNECTED"
    PLATFORM_DISCONNECTED = "PLATFORM_DISCONNECTED"
    MODEL_PROMOTED = "MODEL_PROMOTED"
    SETTINGS_UPDATED = "SETTINGS_UPDATED"
    RATE_LIMIT_BLOCKED = "RATE_LIMIT_BLOCKED"


@dataclass
class AuditEvent:
    event_type: AuditEventType
    user_id: Optional[str]
    ip_address: Optional[str]
    action: str
    target_resource: str
    status: str  # "SUCCESS", "FAILURE", "WARNING"
    details: Dict[str, Any]
    timestamp: datetime


class AuditLogger:
    """Emits structured audit log entries for SIEM and security monitoring."""

    def __init__(self, logger_name: str = "aismm.audit"):
        self.logger = logging.getLogger(logger_name)

    def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        action: str = "",
        target_resource: str = "",
        status: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Create and emit an audit event."""
        event = AuditEvent(
            event_type=event_type,
            user_id=user_id or "anonymous",
            ip_address=ip_address or "127.0.0.1",
            action=action or event_type.value,
            target_resource=target_resource,
            status=status,
            details=details or {},
            timestamp=datetime.now(timezone.utc),
        )

        payload = {
            "audit_event": event.event_type.value,
            "user_id": event.user_id,
            "ip_address": event.ip_address,
            "action": event.action,
            "target_resource": event.target_resource,
            "status": event.status,
            "details": event.details,
            "timestamp": event.timestamp.isoformat(),
        }

        self.logger.info(json.dumps(payload))
        return event


# Global audit logger instance
default_audit_logger = AuditLogger()
