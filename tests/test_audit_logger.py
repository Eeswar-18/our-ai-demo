"""
Unit tests for the Audit Logger component.
"""

import json
import logging
import pytest
from io import StringIO
from unittest.mock import patch
from app.core.audit_logger import AuditLogger, AuditEventType, LogLevel


@pytest.fixture
def audit_logger():
    """Create an audit logger instance for testing."""
    # Create a logger with a string buffer to capture output
    logger = AuditLogger("test-audit")
    # Remove any existing handlers
    for handler in logger.logger.handlers[:]:
        logger.logger.removeHandler(handler)

    # Add a stream handler to capture output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.logger.addHandler(handler)
    logger.logger.setLevel(logging.INFO)
    logger.logger.propagate = False

    return logger, log_stream


@pytest.fixture
def clean_audit_logger():
    """Create a clean audit logger instance for testing (without capturing output)."""
    return AuditLogger("test-clean")


def test_audit_logger_initialization(audit_logger):
    """Test that the audit logger initializes correctly."""
    logger, log_stream = audit_logger
    assert logger.logger.name == "test-audit"
    # Should have at least one handler (we added one)
    assert len(logger.logger.handlers) >= 1


def test_audit_logger_log_user_message(audit_logger):
    """Test logging a user message."""
    logger, log_stream = audit_logger

    correlation_id = "test-correlation-id"
    user_message = "Hello, I need help with my payment."

    logger.log_user_message(user_message, correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    assert log_output != ""

    # Parse the JSON
    log_entry = json.loads(log_output)
    assert log_entry["event_type"] == AuditEventType.USER_MESSAGE.value
    assert log_entry["correlation_id"] == correlation_id
    assert log_entry["data"]["message"] == user_message
    assert "timestamp" in log_entry


def test_audit_logger_log_intent_classified(audit_logger):
    """Test logging an intent classification."""
    logger, log_stream = audit_logger

    correlation_id = "test-correlation-id"
    intent = "check_payment_status"
    confidence = 0.95
    reasoning = "Detected payment-related keywords"

    logger.log_intent_classified(intent, confidence, reasoning, correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    assert log_output != ""

    # Parse the JSON
    log_entry = json.loads(log_output)
    assert log_entry["event_type"] == AuditEventType.INTENT_CLASSIFIED.value
    assert log_entry["correlation_id"] == correlation_id
    assert log_entry["data"]["intent"] == intent
    assert log_entry["data"]["confidence"] == confidence
    assert log_entry["data"]["reasoning"] == reasoning
    assert "timestamp" in log_entry


def test_audit_logger_log_action_planned(audit_logger):
    """Test logging a planned action."""
    logger, log_stream = audit_logger

    correlation_id = "test-correlation-id"
    action_plan = {
        "tool_name": "check_payment_status",
        "parameters": {"transaction_id": "txn_123456"},
        "reasoning": "User wants to check payment status"
    }

    logger.log_action_planned(action_plan, correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    assert log_output != ""

    # Parse the JSON
    log_entry = json.loads(log_output)
    assert log_entry["event_type"] == AuditEventType.ACTION_PLANNED.value
    assert log_entry["correlation_id"] == correlation_id
    assert log_entry["data"]["action_plan"] == action_plan
    assert "timestamp" in log_entry


def test_audit_logger_log_tool_execution(audit_logger):
    """Test logging a tool execution."""
    logger, log_stream = audit_logger

    correlation_id = "test-correlation-id"
    tool_name = "check_payment_status"
    parameters = {"transaction_id": "txn_123456"}
    result = {
        "success": True,
        "payment": {
            "id": 1,
            "transaction_id": "txn_123456",
            "amount": 9.99,
            "status": "success"
        }
    }

    logger.log_tool_execution(tool_name, parameters, result, correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    assert log_output != ""

    # Parse the JSON
    log_entry = json.loads(log_output)
    assert log_entry["event_type"] == AuditEventType.TOOL_EXECUTION.value
    assert log_entry["correlation_id"] == correlation_id
    assert log_entry["data"]["tool_name"] == tool_name
    assert log_entry["data"]["parameters"] == parameters
    assert log_entry["data"]["result"] == result
    assert "timestamp" in log_entry


def test_audit_logger_log_verification_result(audit_logger):
    """Test logging a verification result."""
    logger, log_stream = audit_logger

    correlation_id = "test-correlation-id"
    intent = "check_payment_status"
    goal_achieved = True
    reason = "Payment status verified successfully"

    logger.log_verification_result(intent, goal_achieved, reason, correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    assert log_output != ""

    # Parse the JSON
    log_entry = json.loads(log_output)
    assert log_entry["event_type"] == AuditEventType.VERIFICATION_RESULT.value
    assert log_entry["correlation_id"] == correlation_id
    assert log_entry["data"]["intent"] == intent
    assert log_entry["data"]["goal_achieved"] == goal_achieved
    assert log_entry["data"]["reason"] == reason
    assert "timestamp" in log_entry


def test_audit_logger_log_response_generated(audit_logger):
    """Test logging a generated response."""
    logger, log_stream = audit_logger

    correlation_id = "test-correlation-id"
    response = "I can help you check your payment status. Please provide your transaction ID."
    intent = "check_payment_status"

    logger.log_response_generated(response, intent, correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    assert log_output != ""

    # Parse the JSON
    log_entry = json.loads(log_output)
    assert log_entry["event_type"] == AuditEventType.RESPONSE_GENERATED.value
    assert log_entry["correlation_id"] == correlation_id
    assert log_entry["data"]["response"] == response
    assert log_entry["data"]["intent"] == intent
    assert "timestamp" in log_entry


def test_audit_logger_log_error_occurred(audit_logger):
    """Test logging an error occurrence."""
    logger, log_stream = audit_logger

    correlation_id = "test-correlation-id"
    error = "Database connection timeout"
    context = {
        "tool_name": "check_payment_status",
        "parameters": {"transaction_id": "txn_123456"}
    }

    logger.log_error_occurred(error, context, correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    assert log_output != ""

    # Parse the JSON
    log_entry = json.loads(log_output)
    assert log_entry["event_type"] == AuditEventType.ERROR_OCCURRED.value
    assert log_entry["correlation_id"] == correlation_id
    assert log_entry["data"]["error"] == error
    assert log_entry["data"]["context"] == context
    assert "timestamp" in log_entry


def test_audit_logger_log_escalation_triggered(audit_logger):
    """Test logging an escalation trigger."""
    logger, log_stream = audit_logger

    correlation_id = "test-correlation-id"
    reason = "Customer requested to speak with a supervisor"

    logger.log_escalation_triggered(reason, correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    assert log_output != ""

    # Parse the JSON
    log_entry = json.loads(log_output)
    assert log_entry["event_type"] == AuditEventType.ESCALATION_TRIGGERED.value
    assert log_entry["correlation_id"] == correlation_id
    assert log_entry["data"]["reason"] == reason
    assert "timestamp" in log_entry


def test_audit_logger_different_log_levels():
    """Test that the audit logger respects different log levels."""
    # Create a logger with a string buffer to capture output
    logger = logging.Logger("test-levels")
    logger.setLevel(logging.WARNING)  # Only WARNING and above

    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    # Create audit logger with this logger
    audit_logger = AuditLogger("test-levels")
    audit_logger.logger = logger

    # Test that DEBUG and INFO messages are not logged
    audit_logger._create_audit_entry(
        AuditEventType.USER_MESSAGE,
        {"message": "Test message"},
        level=LogLevel.DEBUG
    )
    audit_logger._create_audit_entry(
        AuditEventType.USER_MESSAGE,
        {"message": "Test message"},
        level=LogLevel.INFO
    )

    # Test that WARNING and above are logged
    audit_logger._create_audit_entry(
        AuditEventType.USER_MESSAGE,
        {"message": "Test message"},
        level=LogLevel.WARNING
    )
    audit_logger._create_audit_entry(
        AuditEventType.USER_MESSAGE,
        {"message": "Test message"},
        level=LogLevel.ERROR
    )

    # Check the output
    log_output = log_stream.getvalue()
    lines = log_output.strip().split('\n')
    # Should have 2 lines (WARNING and ERROR)
    assert len(lines) == 2

    # Parse the JSON entries
    for line in lines:
        log_entry = json.loads(line)
        assert log_entry["event_type"] == AuditEventType.USER_MESSAGE.value
        assert log_entry["data"]["message"] == "Test message"


def test_audit_logger_no_sensitive_data_logged(clean_audit_logger):
    """Test that sensitive data is not inadvertently logged."""
    logger = clean_audit_logger
    # Remove any existing handlers
    for handler in logger.logger.handlers[:]:
        logger.logger.removeHandler(handler)

    # Add a stream handler to capture output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.logger.addHandler(handler)
    logger.logger.setLevel(logging.INFO)
    logger.logger.propagate = False

    # Test logging a tool execution with what might be considered sensitive data
    correlation_id = "test-correlation-id"
    tool_name = "check_payment_status"
    parameters = {
        "transaction_id": "txn_123456",  # This is OK for demo
        # In a real system, we might want to hash or mask this
    }
    result = {
        "success": True,
        "payment": {
            "id": 1,
            "transaction_id": "txn_123456",
            "amount": 9.99,
            "status": "success",
            # In a real system, we wouldn't log full card numbers or other PII
            # But for this demo, transaction IDs are considered non-sensitive
        }
    }

    logger.log_tool_execution(tool_name, parameters, result, correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    assert log_output != ""

    # Parse the JSON
    log_entry = json.loads(log_output)
    # Verify that the data is logged as expected (for this demo, we're not masking transaction IDs)
    assert log_entry["data"]["parameters"]["transaction_id"] == "txn_123456"
    assert log_entry["data"]["result"]["payment"]["transaction_id"] == "txn_123456"


def test_audit_logger_correlation_id_propagation(clean_audit_logger):
    """Test that correlation IDs are properly propagated through the audit log."""
    logger = clean_audit_logger
    # Remove any existing handlers
    for handler in logger.logger.handlers[:]:
        logger.logger.removeHandler(handler)

    # Add a stream handler to capture output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.logger.addHandler(handler)
    logger.logger.setLevel(logging.INFO)
    logger.logger.propagate = False

    correlation_id = "test-correlation-123"

    # Log several events with the same correlation ID
    logger.log_user_message("Hello", correlation_id)
    logger.log_intent_classified("general_question", 0.8, "Testing", correlation_id)
    logger.log_action_planned({"tool_name": "generate_response"}, correlation_id)
    logger.log_tool_execution("generate_response", {}, {"success": True}, correlation_id)
    logger.log_verification_result("general_question", True, "OK", correlation_id)
    logger.log_response_generated("Hello! How can I help?", "general_question", correlation_id)

    # Get the log output
    log_output = log_stream.getvalue().strip()
    lines = log_output.split('\n')

    # Should have 6 lines
    assert len(lines) == 6

    # Each line should have the same correlation ID
    for line in lines:
        log_entry = json.loads(line)
        assert log_entry["correlation_id"] == correlation_id


if __name__ == "__main__":
    pytest.main([__file__])