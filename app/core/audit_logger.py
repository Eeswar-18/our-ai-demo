"""
Audit Logger component for the our-ai-demo V0.
Provides structured logging of all agent operations for transparency and debugging.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AuditEventType(Enum):
    USER_MESSAGE = "USER_MESSAGE"
    INTENT_CLASSIFIED = "INTENT_CLASSIFIED"
    ACTION_PLANNED = "ACTION_PLANNED"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    VERIFICATION_RESULT = "VERIFICATION_RESULT"
    RESPONSE_GENERATED = "RESPONSE_GENERATED"
    ERROR_OCCURRED = "ERROR_OCCURRED"
    ESCALATION_TRIGGERED = "ESCALATION_TRIGGERED"


class AuditLogger:
    """Structured audit logger for tracking agent operations."""
    # Class-level log storage for retrieval via API
    _log_store = []
    _max_logs = 1000  # Maximum number of logs to keep in memory

    def __init__(self, name: str = "our-ai-demo-audit"):
        self.logger = logging.getLogger(name)
        # Ensure the logger has a handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        # Prevent propagation to root logger to avoid duplicate logs
        self.logger.propagate = False

    def _create_audit_entry(
        self,
        event_type: AuditEventType,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        level: LogLevel = LogLevel.INFO
    ) -> str:
        """
        Create a structured audit log entry.

        Args:
            event_type: The type of audit event
            data: The data to log
            correlation_id: Optional correlation ID for tracing related events
            level: The log level

        Returns:
            JSON string of the audit entry
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type.value,
            "correlation_id": correlation_id,
            "data": data
        }

        json_entry = json.dumps(entry)

        # Store the log entry for retrieval
        AuditLogger._log_store.append(json_entry)
        # Trim if exceeds max logs
        if len(AuditLogger._log_store) > AuditLogger._max_logs:
            AuditLogger._log_store = AuditLogger._log_store[-AuditLogger._max_logs:]

        # Log at the appropriate level
        if level == LogLevel.DEBUG:
            self.logger.debug(json_entry)
        elif level == LogLevel.INFO:
            self.logger.info(json_entry)
        elif level == LogLevel.WARNING:
            self.logger.warning(json_entry)
        elif level == LogLevel.ERROR:
            self.logger.error(json_entry)

        return json_entry

    def log_user_message(self, user_message: str, correlation_id: Optional[str] = None) -> str:
        """Log a user message."""
        return self._create_audit_entry(
            AuditEventType.USER_MESSAGE,
            {"message": user_message},
            correlation_id
        )

    def log_intent_classified(
        self,
        intent: str,
        confidence: float,
        reasoning: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log an intent classification result."""
        return self._create_audit_entry(
            AuditEventType.INTENT_CLASSIFIED,
            {
                "intent": intent,
                "confidence": confidence,
                "reasoning": reasoning
            },
            correlation_id
        )

    def log_action_planned(
        self,
        action_plan: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log a planned action."""
        return self._create_audit_entry(
            AuditEventType.ACTION_PLANNED,
            {"action_plan": action_plan},
            correlation_id
        )

    def log_tool_execution(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log a tool execution and its result."""
        return self._create_audit_entry(
            AuditEventType.TOOL_EXECUTION,
            {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result
            },
            correlation_id
        )

    def log_verification_result(
        self,
        intent: str,
        goal_achieved: bool,
        reason: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log a verification result."""
        return self._create_audit_entry(
            AuditEventType.VERIFICATION_RESULT,
            {
                "intent": intent,
                "goal_achieved": goal_achieved,
                "reason": reason
            },
            correlation_id
        )

    def log_response_generated(
        self,
        response: str,
        intent: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log a generated response."""
        return self._create_audit_entry(
            AuditEventType.RESPONSE_GENERATED,
            {
                "response": response,
                "intent": intent
            },
            correlation_id
        )

    def log_error_occurred(
        self,
        error: str,
        context: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log an error that occurred during processing."""
        return self._create_audit_entry(
            AuditEventType.ERROR_OCCURRED,
            {
                "error": error,
                "context": context
            },
            correlation_id,
            LogLevel.ERROR
        )

    def log_escalation_triggered(
        self,
        reason: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log that escalation was triggered."""
        return self._create_audit_entry(
            AuditEventType.ESCALATION_TRIGGERED,
            {"reason": reason},
            correlation_id
        )

    @classmethod
    def get_recent_logs(cls, limit: int = 100) -> list:
        """Return the most recent audit log entries.
        Args:
            limit: Maximum number of logs to return
        Returns:
            List of JSON strings (most recent first)
        """
        # Return the most recent logs, up to limit
        return list(reversed(cls._log_store))[:limit]
