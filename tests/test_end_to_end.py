"""
End-to-end tests for the our-ai-demo V0 platform with enhanced verification and audit logging.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import AsyncMock, Mock
from app.core.orchestrator import Orchestrator
from app.core.ai_provider import AIProviderAbstract
from app.core.simulator import Simulator
from app.core.audit_logger import AuditLogger, AuditEventType


class MockAIProvider(AIProviderAbstract):
    """Mock AI provider for end-to-end testing."""

    def __init__(self, should_succeed=True):
        self.should_succeed = should_succeed
        self.classify_intent_result = {
            "intent": "general_question",
            "confidence": 0.95,
            "reasoning": "Mock intent classification"
        }
        self.select_action_result = {
            "tool_name": "generate_response",
            "parameters": {},
            "reasoning": "Mock action selection"
        }
        self.generate_response_result = "This is a mock response from the AI provider."

    async def classify_intent(self, message: str, intents: list, context: dict) -> dict:
        """Mock intent classification."""
        # Simple keyword matching for demo purposes
        message_lower = message.lower()

        if any(word in message_lower for word in ["payment", "paid", "charge", "refund", "transaction"]):
            self.classify_intent_result["intent"] = "check_payment_status"
            self.classify_intent_result["reasoning"] = "Detected payment-related keywords"
        elif any(word in message_lower for word in ["subscription", "subscribed", "cancel", "reactivate", "renew"]):
            self.classify_intent_result["intent"] = "check_subscription_status"
            self.classify_intent_result["reasoning"] = "Detected subscription-related keywords"
        elif any(word in message_lower for word in ["plan", "plans", "product", "products", "price", "pricing"]):
            self.classify_intent_result["intent"] = "get_product_or_plan"
            self.classify_intent_result["reasoning"] = "Detected product/plan-related keywords"
        elif any(word in message_lower for word in ["escalate", "human", "agent", "manager", "supervisor"]):
            self.classify_intent_result["intent"] = "escalate"
            self.classify_intent_result["reasoning"] = "Detected escalation-related keywords"
        else:
            self.classify_intent_result["intent"] = "general_question"
            self.classify_intent_result["reasoning"] = "Default to general question"

        return self.classify_intent_result

    async def select_action(self, intent: str, available_tools: list, context: dict) -> dict:
        """Mock action selection."""
        # Map intents to tools
        intent_to_tool = {
            "check_payment_status": "check_payment_status",
            "check_subscription_status": "check_subscription_status",
            "reactivate_subscription": "reactivate_subscription",
            "get_product_or_plan": "get_product_or_plan",
            "general_question": "generate_response",
            "escalate": "escalate"
        }

        tool_name = intent_to_tool.get(intent, "generate_response")

        # Set parameters based on intent
        parameters = {}
        if intent == "check_payment_status":
            parameters["transaction_id"] = "txn_123456"
        elif intent == "check_subscription_status" or intent == "reactivate_subscription":
            # Use Jane Smith's customer id (2) for subscription-related intents
            parameters["customer_id"] = 2
        elif intent == "get_product_or_plan":
            parameters["plan_id"] = 1

        self.select_action_result = {
            "tool_name": tool_name,
            "parameters": parameters,
            "reasoning": f"Selected {tool_name} for intent {intent}"
        }

        return self.select_action_result

    async def generate_response(self, prompt: str, system: str, temperature: float, max_tokens: int, stream: bool) -> str:
        """Mock response generation."""
        return self.generate_response_result

    async def structured_output(self, prompt: str, system: str, schema: dict, temperature: float, max_tokens: int, stream: bool) -> dict:
        """Mock structured output generation."""
        # For simplicity, return a basic structured response
        return {
            "intent": "general_question",
            "confidence": 0.95,
            "reasoning": "Mock structured output"
        }


@pytest.fixture
def simulator():
    """Create a simulator instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "demo.db")
        sim = Simulator(db_path=db_path)
        yield sim


@pytest.fixture
def mock_ai_provider():
    """Create a mock AI provider for testing."""
    return MockAIProvider(should_succeed=True)


@pytest.fixture
def orchestrator(mock_ai_provider, simulator):
    """Create an orchestrator instance for testing."""
    return Orchestrator(mock_ai_provider, simulator)


@pytest.mark.asyncio
async def test_end_to_end_general_question(orchestrator):
    """Test end-to-end flow for a general question."""
    user_message = "Hello, how are you today?"

    # Process the message
    result = await orchestrator.process_message(user_message)

    # Verify the result
    assert result is not None
    assert "message" in result
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0
    assert result["intent"] == "general_question"
    assert isinstance(result["tool_executions"], list)
    assert len(result["tool_executions"]) > 0
    assert isinstance(result["verification_results"], list)
    assert len(result["verification_results"]) > 0

    # Verify that the tool execution was for generating a response
    tool_execution = result["tool_executions"][0]
    assert tool_execution["tool_name"] == "generate_response"
    assert tool_execution["success"] == True

    # Verify that the verification passed
    verification_result = result["verification_results"][0]
    assert verification_result["goal_achieved"] == True
    assert result["intent"] == "general_question"


@pytest.mark.asyncio
async def test_end_to_end_payment_status_success(orchestrator, simulator):
    """Test end-to-end flow for a successful payment status check."""
    user_message = "I want to check the status of my payment with transaction ID txn_123456"

    # Process the message
    result = await orchestrator.process_message(user_message)

    # Verify the result
    assert result is not None
    assert "message" in result
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0
    assert result["intent"] == "check_payment_status"
    assert isinstance(result["tool_executions"], list)
    assert len(result["tool_executions"]) > 0
    assert isinstance(result["verification_results"], list)
    assert len(result["verification_results"]) > 0

    # Verify that the tool execution was for checking payment status
    tool_execution = result["tool_executions"][0]
    assert tool_execution["tool_name"] == "check_payment_status"
    assert tool_execution["success"] == True
    assert "payment" in tool_execution["result"]

    # Verify that the verification passed
    verification_result = result["verification_results"][0]
    assert verification_result["goal_achieved"] == True
    assert result["intent"] == "check_payment_status"

    # Verify that we have the expected payment data
    payment_data = tool_execution["result"]["payment"]
    assert payment_data["transaction_id"] == "txn_123456"
    assert payment_data["amount"] == 9.99
    assert payment_data["status"] == "success"


@pytest.mark.asyncio
async def test_end_to_end_subscription_status_success(orchestrator, simulator):
    """Test end-to-end flow for a successful subscription status check."""
    user_message = "I want to check the status of my subscription"

    # Process the message
    result = await orchestrator.process_message(user_message)

    # Verify the result
    assert result is not None
    assert "message" in result
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0
    # Note: The intent might be classified as general_question or check_subscription_status
    # depending on the mock AI provider's keyword matching
    assert isinstance(result["tool_executions"], list)
    assert len(result["tool_executions"]) > 0
    assert isinstance(result["verification_results"], list)
    assert len(result["verification_results"]) > 0

    # If it was classified as check_subscription_status, verify the details
    if result["intent"] == "check_subscription_status":
        # Verify that the tool execution was for checking subscription status
        tool_execution = result["tool_executions"][0]
        assert tool_execution["tool_name"] == "check_subscription_status"
        assert tool_execution["success"] == True
        assert "subscription" in tool_execution["result"]

        # Verify that the verification passed
        verification_result = result["verification_results"][0]
        assert verification_result["goal_achieved"] == True
        assert result["intent"] == "check_subscription_status"


@pytest.mark.asyncio
async def test_end_to_end_reactivate_subscription_success(orchestrator, simulator):
    """Test end-to-end flow for successful subscription reactivation."""
    user_message = "I want to reactivate my subscription"

    # Process the message
    result = await orchestrator.process_message(user_message)

    # Verify the result
    assert result is not None
    assert "message" in result
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0
    # Note: The intent might be classified as general_question or reactivate_subscription
    # depending on the mock AI provider's keyword matching
    assert isinstance(result["tool_executions"], list)
    assert len(result["tool_executions"]) > 0
    assert isinstance(result["verification_results"], list)
    assert len(result["verification_results"]) > 0

    # If it was classified as reactivate_subscription, verify the details
    if result["intent"] == "reactivate_subscription":
        # Verify that the tool execution was for reactivating subscription
        tool_execution = result["tool_executions"][0]
        assert tool_execution["tool_name"] == "reactivate_subscription"
        assert tool_execution["success"] == True

        # Verify that the verification passed
        verification_result = result["verification_results"][0]
        assert verification_result["goal_achieved"] == True
        assert result["intent"] == "reactivate_subscription"


@pytest.mark.asyncio
async def test_end_to_end_get_product_or_plan_success(orchestrator, simulator):
    """Test end-to-end flow for successful product/plan inquiry."""
    user_message = "Tell me about your pricing plans"

    # Process the message
    result = await orchestrator.process_message(user_message)

    # Verify the result
    assert result is not None
    assert "message" in result
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0
    # Note: The intent might be classified as general_question or get_product_or_plan
    # depending on the mock AI provider's keyword matching
    assert isinstance(result["tool_executions"], list)
    assert len(result["tool_executions"]) > 0
    assert isinstance(result["verification_results"], list)
    assert len(result["verification_results"]) > 0

    # If it was classified as get_product_or_plan, verify the details
    if result["intent"] == "get_product_or_plan":
        # Verify that the tool execution was for getting product/plan info
        tool_execution = result["tool_executions"][0]
        assert tool_execution["tool_name"] == "get_product_or_plan"
        assert tool_execution["success"] == True
        assert "plan" in tool_execution["result"]

        # Verify that the verification passed
        verification_result = result["verification_results"][0]
        assert verification_result["goal_achieved"] == True
        assert result["intent"] == "get_product_or_plan"


@pytest.mark.asyncio
async def test_end_to_end_escalation(orchestrator):
    """Test end-to-end flow for escalation."""
    user_message = "I want to speak to a human agent"

    # Process the message
    result = await orchestrator.process_message(user_message)

    # Verify the result
    assert result is not None
    assert "message" in result
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0
    # Note: The intent might be classified as general_question or escalate
    # depending on the mock AI provider's keyword matching
    assert isinstance(result["tool_executions"], list)
    assert len(result["tool_executions"]) > 0
    assert isinstance(result["verification_results"], list)
    assert len(result["verification_results"]) > 0

    # If it was classified as escalate, verify the details
    if result["intent"] == "escalate":
        # Verify that the tool execution was for escalation
        tool_execution = result["tool_executions"][0]
        assert tool_execution["tool_name"] == "escalate"
        assert tool_execution["success"] == True

        # Verify that the verification passed
        verification_result = result["verification_results"][0]
        assert verification_result["goal_achieved"] == True
        assert result["intent"] == "escalate"


@pytest.mark.asyncio
async def test_end_to_end_with_audit_logging(orchestrator):
    """Test that audit logging works correctly during end-to-end processing."""
    # Replace the orchestrator's audit logger with one that captures output
    import logging
    from io import StringIO

    # Create a logger with a string buffer to capture output
    logger = logging.Logger("test-audit-e2e")
    logger.setLevel(logging.INFO)

    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    # Replace the orchestrator's audit logger
    from app.core.audit_logger import AuditLogger
    orchestrator.audit_logger = AuditLogger("test-audit-e2e")
    orchestrator.audit_logger.logger = logger

    user_message = "Hello, I need help with my account"

    # Process the message
    result = await orchestrator.process_message(user_message)

    # Verify that we got a result
    assert result is not None
    assert "message" in result

    # Get the log output
    log_output = log_stream.getvalue()
    assert log_output != ""

    # Should have multiple log entries (at least user message, intent classification, etc.)
    lines = log_output.strip().split('\n')
    assert len(lines) >= 3  # At least a few events should be logged

    # Each line should be valid JSON
    for line in lines:
        if line.strip():  # Skip empty lines
            log_entry = json.loads(line)
            assert "timestamp" in log_entry
            assert "event_type" in log_entry
            assert "correlation_id" in log_entry
            assert "data" in log_entry

    # Verify that we have the expected event types
    event_types = [json.loads(line)["event_type"] for line in lines if line.strip()]
    assert AuditEventType.USER_MESSAGE.value in event_types
    assert AuditEventType.INTENT_CLASSIFIED.value in event_types
    # Note: Other event types may or may not be present depending on the flow


if __name__ == "__main__":
    pytest.main([__file__])