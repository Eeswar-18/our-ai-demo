"""
Test chat endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock


def test_chat_endpoint_general_question():
    """Test the chat endpoint with a general question."""
    from app.main import app
    from app.api.v1 import chat
    from app.core.orchestrator import Orchestrator

    # Create mocks
    mock_ai_provider = Mock()
    mock_ai_provider.classify_intent = AsyncMock(return_value={"intent": "general_question", "confidence": 0.9, "reasoning": "General question"})
    mock_ai_provider.select_action = AsyncMock(return_value={
        "tool_name": "general_question",
        "parameters": {},
        "reasoning": "No tool needed"
    })
    mock_ai_provider.generate_response = AsyncMock(return_value="This is a test response.")
    mock_ai_provider.structured_output = AsyncMock(return_value={})

    mock_simulator = Mock()

    mock_orchestrator = Mock(spec=Orchestrator)
    mock_orchestrator.process_message = AsyncMock(return_value={
        "message": "This is a test response from the orchestrator.",
        "intent": "general_question",
        "tool_executions": [],
        "verification_results": []
    })

    # Set the globals in the chat module to our mocks
    chat._ai_provider = mock_ai_provider
    chat._simulator = mock_simulator
    chat._orchestrator = mock_orchestrator

    # Create the test client
    client = TestClient(app)

    # Make the request
    response = client.post("/v1/chat", json={"message": "Hello, how are you?"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "This is a test response from the orchestrator."
    assert data["intent"] == "general_question"

    # Reset the globals
    chat._ai_provider = None
    chat._simulator = None
    chat._orchestrator = None


def test_chat_endpoint_payment_status():
    """Test the chat endpoint for a payment status inquiry."""
    from app.main import app
    from app.api.v1 import chat
    from app.core.orchestrator import Orchestrator

    # Create mocks
    mock_ai_provider = Mock()
    mock_ai_provider.classify_intent = AsyncMock(return_value={"intent": "check_payment_status", "confidence": 0.95, "reasoning": "User wants to check payment status"})
    mock_ai_provider.select_action = AsyncMock(return_value={
        "tool_name": "check_payment_status",
        "parameters": {"transaction_id": "txn_123456"},
        "reasoning": "User provided a transaction ID"
    })
    mock_ai_provider.generate_response = AsyncMock(return_value="I checked your payment with transaction ID txn_123456. It was successful for $9.99.")
    mock_ai_provider.structured_output = AsyncMock(return_value={})

    mock_simulator = Mock()
    mock_simulator.get_payment_by_transaction_id = Mock(return_value={
        "id": 1,
        "customer_id": 1,
        "transaction_id": "txn_123456",
        "amount": 9.99,
        "status": "success",
        "payment_date": "2026-01-01 00:00:00"
    })

    mock_orchestrator = Mock(spec=Orchestrator)
    mock_orchestrator.process_message = AsyncMock(return_value={
        "message": "I checked your payment with transaction ID txn_123456. It was successful for $9.99.",
        "intent": "check_payment_status",
        "tool_executions": [{"tool_name": "check_payment_status", "success": True, "result": {"payment": {"status": "success", "amount": 9.99}}}],
        "verification_results": [{"goal_achieved": True, "reason": "Payment status retrieved successfully"}]
    })

    # Set the globals in the chat module to our mocks
    chat._ai_provider = mock_ai_provider
    chat._simulator = mock_simulator
    chat._orchestrator = mock_orchestrator

    # Create the test client
    client = TestClient(app)

    # Make the request
    response = client.post("/v1/chat", json={"message": "I paid with transaction ID txn_123456. Was it successful?"})
    assert response.status_code == 200
    data = response.json()
    assert "txn_123456" in data["message"]
    assert data["intent"] == "check_payment_status"
    mock_orchestrator.process_message.assert_called_once()

    # Reset the globals
    chat._ai_provider = None
    chat._simulator = None
    chat._orchestrator = None


def test_chat_endpoint_error():
    """Test the chat endpoint when an error occurs."""
    from app.main import app
    from app.api.v1 import chat
    from app.core.orchestrator import Orchestrator

    # Create mocks
    mock_ai_provider = Mock()
    mock_ai_provider.classify_intent = AsyncMock(return_value={"intent": "general_question", "confidence": 0.9, "reasoning": "General question"})
    mock_ai_provider.select_action = AsyncMock(return_value={
        "tool_name": "general_question",
        "parameters": {},
        "reasoning": "No tool needed"
    })
    mock_ai_provider.generate_response = AsyncMock(return_value="This is a test response.")
    mock_ai_provider.structured_output = AsyncMock(return_value={})

    mock_simulator = Mock()

    mock_orchestrator = Mock(spec=Orchestrator)
    mock_orchestrator.process_message = AsyncMock(side_effect=Exception("Test error"))

    # Set the globals in the chat module to our mocks
    chat._ai_provider = mock_ai_provider
    chat._simulator = mock_simulator
    chat._orchestrator = mock_orchestrator

    # Create the test client
    client = TestClient(app)

    # Make the request
    response = client.post("/v1/chat", json={"message": "This will cause an error"})
    assert response.status_code == 500
    assert "An internal error occurred. Please try again or contact support." == response.json()["detail"]

    # Reset the globals
    chat._ai_provider = None
    chat._simulator = None
    chat._orchestrator = None


def test_chat_endpoint_business_question():
    """Test the chat endpoint with a business question."""
    from app.main import app
    from app.api.v1 import chat
    from app.core.orchestrator import Orchestrator
    from app.core.simulator import Simulator

    # Create mocks for AI provider
    mock_ai_provider = Mock()
    mock_ai_provider.classify_intent = AsyncMock(return_value={"intent": "general_question", "confidence": 0.9, "reasoning": "General question"})
    mock_ai_provider.select_action = AsyncMock(return_value={
        "tool_name": "general_question",
        "parameters": {},
        "reasoning": "No tool needed"
    })
    # We want to capture the prompt passed to generate_response
    prompt_captured = None
    async def capture_prompt(prompt, system, temperature, max_tokens, stream):
        nonlocal prompt_captured
        prompt_captured = prompt
        return "This is a test response."
    mock_ai_provider.generate_response = AsyncMock(side_effect=capture_prompt)
    mock_ai_provider.structured_output = AsyncMock(return_value={})

    # Create a real simulator (we can use the real one because we won't execute any tools)
    mock_simulator = Simulator()

    # Create a real orchestrator with the mocked AI provider and real simulator
    mock_orchestrator = Orchestrator(mock_ai_provider, mock_simulator)

    # Set the globals in the chat module to our mocks
    chat._ai_provider = mock_ai_provider
    chat._simulator = mock_simulator
    chat._orchestrator = mock_orchestrator

    # Create the test client
    client = TestClient(app)

    # Make the request with a business question
    response = client.post("/v1/chat", json={"message": "What are your business hours?"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "This is a test response."
    assert data["intent"] == "general_question"

    # Check that the prompt captured by generate_response contains the business context
    assert prompt_captured is not None
    assert "Business Information:" in prompt_captured
    assert "Our AI Demo Business" in prompt_captured
    assert "Standard support is available during business hours (9 AM - 5 PM EST)" in prompt_captured

    # Reset the globals
    chat._ai_provider = None
    chat._simulator = None
    chat._orchestrator = None