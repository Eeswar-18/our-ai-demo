"""
Unit tests for the Verifier component.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock
from app.core.verifier import Verifier
from app.core.simulator import Simulator


@pytest.fixture
def simulator():
    """Create a simulator instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "demo.db")
        sim = Simulator(db_path=db_path)
        yield sim


@pytest.fixture
def verifier(simulator):
    """Create a verifier instance for testing."""
    return Verifier(simulator)


def test_verifier_payment_status_success(verifier, simulator):
    """Test verification of successful payment status check."""
    # First, check that we have the demo data loaded
    payment = simulator.get_payment_by_transaction_id("txn_123456")
    assert payment is not None
    assert payment["status"] == "success"

    # Test successful verification
    tool_result = {
        "success": True,
        "tool_name": "check_payment_status",
        "parameters": {"transaction_id": "txn_123456"},
        "result": {
            "success": True,
            "payment": payment
        }
    }

    verification_result = verifier.verify_payment_status("txn_123456", tool_result)
    assert verification_result["goal_achieved"] == True
    assert "verified successfully" in verification_result["reason"]


def test_verifier_payment_status_failed_tool(verifier):
    """Test verification when the tool itself fails."""
    tool_result = {
        "success": False,
        "error": "Database connection failed"
    }

    verification_result = verifier.verify_payment_status("txn_123456", tool_result)
    assert verification_result["goal_achieved"] == False
    assert "Tool failed" in verification_result["reason"]


def test_verifier_payment_status_no_data(verifier):
    """Test verification when tool succeeds but returns no data."""
    tool_result = {
        "success": True,
        "result": {
            "payment": None
        }
    }

    verification_result = verifier.verify_payment_status("txn_123456", tool_result)
    assert verification_result["goal_achieved"] == False
    assert "returned no payment data" in verification_result["reason"]


def test_verifier_payment_status_wrong_data(verifier, simulator):
    """Test verification when tool returns incorrect data."""
    # Get the actual payment from simulator
    actual_payment = simulator.get_payment_by_transaction_id("txn_123456")
    assert actual_payment is not None

    # Create a tool result with wrong data
    wrong_payment = actual_payment.copy()
    wrong_payment["amount"] = 999.99  # Wrong amount

    tool_result = {
        "success": True,
        "result": {
            "payment": wrong_payment
        }
    }

    verification_result = verifier.verify_payment_status("txn_123456", tool_result)
    assert verification_result["goal_achieved"] == False
    assert "mismatch" in verification_result["reason"]


def test_verifier_subscription_status_success(verifier, simulator):
    """Test verification of successful subscription status check."""
    # Get a customer with an inactive subscription (Jane Smith)
    customer = simulator.get_customer_by_email("jane.smith@example.com")
    assert customer is not None
    customer_id = customer["id"]

    # Get the actual subscription from simulator
    actual_subscription = simulator.get_subscription_by_customer_id(customer_id)
    assert actual_subscription is not None
    assert actual_subscription["status"] == "inactive"

    # Test successful verification
    tool_result = {
        "success": True,
        "result": {
            "subscription": actual_subscription
        }
    }

    verification_result = verifier.verify_subscription_status(customer_id, tool_result)
    assert verification_result["goal_achieved"] == True
    assert "verified successfully" in verification_result["reason"]


def test_verifier_subscription_status_failed_tool(verifier):
    """Test verification when the tool itself fails."""
    tool_result = {
        "success": False,
        "error": "Database connection failed"
    }

    verification_result = verifier.verify_subscription_status(1, tool_result)
    assert verification_result["goal_achieved"] == False
    assert "Tool failed" in verification_result["reason"]


def test_verifier_subscription_status_no_data(verifier):
    """Test verification when tool succeeds but returns no data."""
    tool_result = {
        "success": True,
        "result": {
            "subscription": None
        }
    }

    verification_result = verifier.verify_subscription_status(1, tool_result)
    assert verification_result["goal_achieved"] == False
    assert "returned no subscription data" in verification_result["reason"]


def test_verifier_subscription_status_wrong_data(verifier, simulator):
    """Test verification when tool returns incorrect data."""
    # Get a customer with an inactive subscription (Jane Smith)
    customer = simulator.get_customer_by_email("jane.smith@example.com")
    assert customer is not None
    customer_id = customer["id"]

    # Get the actual subscription from simulator
    actual_subscription = simulator.get_subscription_by_customer_id(customer_id)
    assert actual_subscription is not None

    # Create a tool result with wrong data
    wrong_subscription = actual_subscription.copy()
    wrong_subscription["status"] = "active"  # Wrong status

    tool_result = {
        "success": True,
        "result": {
            "subscription": wrong_subscription
        }
    }

    verification_result = verifier.verify_subscription_status(customer_id, tool_result)
    assert verification_result["goal_achieved"] == False
    assert "mismatch" in verification_result["reason"]


def test_verifier_reactivate_subscription_success(verifier, simulator):
    """Test verification of successful subscription reactivation."""
    # Get a customer with an inactive subscription (Jane Smith)
    customer = simulator.get_customer_by_email("jane.smith@example.com")
    assert customer is not None
    customer_id = customer["id"]

    # Verify the subscription is initially inactive
    actual_subscription = simulator.get_subscription_by_customer_id(customer_id)
    assert actual_subscription is not None
    assert actual_subscription["status"] == "inactive"

    # Manually update the subscription to active in the simulator to simulate the tool having worked
    # In a real test, we would mock the tool to return success and then verify the state changed
    # For this test, we'll directly set it to active to simulate what the tool should have done
    conn = simulator._get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE subscriptions SET status = 'active' WHERE customer_id = ?",
            (customer_id,)
        )
        conn.commit()
    finally:
        simulator._execute_and_close(conn)

    # Now verify that it's active
    actual_subscription = simulator.get_subscription_by_customer_id(customer_id)
    assert actual_subscription["status"] == "active"

    # Test successful verification
    tool_result = {
        "success": True,
        "result": {
            "subscription": actual_subscription
        }
    }

    verification_result = verifier.verify_reactivate_subscription(customer_id, tool_result)
    assert verification_result["goal_achieved"] == True
    assert "verified successfully" in verification_result["reason"]


def test_verifier_reactivate_subscription_failed_tool(verifier):
    """Test verification when the tool itself fails."""
    tool_result = {
        "success": False,
        "error": "Database connection failed"
    }

    verification_result = verifier.verify_reactivate_subscription(1, tool_result)
    assert verification_result["goal_achieved"] == False
    assert "Tool failed" in verification_result["reason"]


def test_verifier_get_product_or_plan_success(verifier, simulator):
    """Test verification of successful plan retrieval."""
    # Get a plan from the simulator
    plan = simulator.get_plan_by_id(1)
    assert plan is not None
    assert plan["name"] == "Basic"

    # Test successful verification
    tool_result = {
        "success": True,
        "result": {
            "plan": plan
        }
    }

    verification_result = verifier.verify_get_product_or_plan(1, tool_result)
    assert verification_result["goal_achieved"] == True
    assert "verified successfully" in verification_result["reason"]


def test_verifier_get_product_or_plan_failed_tool(verifier):
    """Test verification when the tool itself fails."""
    tool_result = {
        "success": False,
        "error": "Database connection failed"
    }

    verification_result = verifier.verify_get_product_or_plan(1, tool_result)
    assert verification_result["goal_achieved"] == False
    assert "Tool failed" in verification_result["reason"]


def test_verifier_get_product_or_plan_no_data(verifier):
    """Test verification when tool succeeds but returns no data."""
    tool_result = {
        "success": True,
        "result": {
            "plan": None
        }
    }

    verification_result = verifier.verify_get_product_or_plan(1, tool_result)
    assert verification_result["goal_achieved"] == False
    assert "returned no plan data" in verification_result["reason"]


def test_verifier_get_product_or_plan_wrong_data(verifier, simulator):
    """Test verification when tool returns incorrect data."""
    # Get the actual plan from simulator
    actual_plan = simulator.get_plan_by_id(1)
    assert actual_plan is not None

    # Create a tool result with wrong data
    wrong_plan = actual_plan.copy()
    wrong_plan["price"] = 999.99  # Wrong price

    tool_result = {
        "success": True,
        "result": {
            "plan": wrong_plan
        }
    }

    verification_result = verifier.verify_get_product_or_plan(1, tool_result)
    assert verification_result["goal_achieved"] == False
    assert "mismatch" in verification_result["reason"]


def test_verifier_general_question_success(verifier):
    """Test verification of successful general question response generation."""
    tool_result = {
        "success": True,
        "result": {
            "response_generated": True
        }
    }

    verification_result = verifier.verify_general_question(tool_result)
    assert verification_result["goal_achieved"] == True
    assert "generated successfully" in verification_result["reason"]


def test_verifier_general_question_failure(verifier):
    """Test verification of failed general question response generation."""
    tool_result = {
        "success": False,
        "error": "Failed to generate response"
    }

    verification_result = verifier.verify_general_question(tool_result)
    assert verification_result["goal_achieved"] == False
    assert "Failed to generate response" in verification_result["reason"]


def test_verifier_general_question_no_response_flag(verifier):
    """Test verification when tool succeeds but didn't generate response."""
    tool_result = {
        "success": True,
        "result": {
            "response_generated": False  # This is the key difference
        }
    }

    verification_result = verifier.verify_general_question(tool_result)
    assert verification_result["goal_achieved"] == False
    assert "Failed to generate response" in verification_result["reason"]


def test_verifier_escalate_success(verifier):
    """Test verification of successful escalation."""
    tool_result = {
        "success": True
    }

    verification_result = verifier.verify_escalate(tool_result)
    assert verification_result["goal_achieved"] == True
    assert "processed successfully" in verification_result["reason"]


def test_verifier_escalate_failure(verifier):
    """Test verification of failed escalation."""
    tool_result = {
        "success": False,
        "error": "Failed to escalate"
    }

    verification_result = verifier.verify_escalate(tool_result)
    assert verification_result["goal_achieved"] == False
    assert "Tool failed: Failed to escalate" in verification_result["reason"]


def test_verifier_unknown_intent(verifier):
    """Test verification with an unknown intent."""
    tool_result = {
        "success": True
    }

    verification_result = verifier.verify_action("unknown_intent", tool_result)
    assert verification_result["goal_achieved"] == False
    assert "Unknown intent" in verification_result["reason"]


def test_verifier_main_method_routes_correctly(verifier, simulator):
    """Test that the main verify_action method routes to the correct verifier."""
    # Test payment verification routing
    payment = simulator.get_payment_by_transaction_id("txn_123456")
    tool_result = {
        "success": True,
        "result": {
            "payment": payment
        }
    }
    result = verifier.verify_action("check_payment_status", tool_result, transaction_id="txn_123456")
    assert result["goal_achieved"] == True

    # Test subscription verification routing
    customer = simulator.get_customer_by_email("jane.smith@example.com")
    customer_id = customer["id"]
    subscription = simulator.get_subscription_by_customer_id(customer_id)
    tool_result = {
        "success": True,
        "result": {
            "subscription": subscription
        }
    }
    result = verifier.verify_action("check_subscription_status", tool_result, customer_id=customer_id)
    assert result["goal_achieved"] == True

    # Test reactivation verification routing
    tool_result = {
        "success": True,
        "result": {
            "subscription": subscription
        }
    }
    # First make it inactive then active for this test
    conn = simulator._get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE subscriptions SET status = 'active' WHERE customer_id = ?",
            (customer_id,)
        )
        conn.commit()
    finally:
        simulator._execute_and_close(conn)
    result = verifier.verify_action("reactivate_subscription", tool_result, customer_id=customer_id)
    assert result["goal_achieved"] == True

    # Test product/plan verification routing
    plan = simulator.get_plan_by_id(1)
    tool_result = {
        "success": True,
        "result": {
            "plan": plan
        }
    }
    result = verifier.verify_action("get_product_or_plan", tool_result, plan_id=1)
    assert result["goal_achieved"] == True

    # Test general question verification routing
    tool_result = {
        "success": True,
        "result": {"response_generated": True}
    }
    result = verifier.verify_action("general_question", tool_result)
    assert result["goal_achieved"] == True

    # Test escalate verification routing
    tool_result = {
        "success": True
    }
    result = verifier.verify_action("escalate", tool_result)
    assert result["goal_achieved"] == True