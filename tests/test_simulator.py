"""
Test simulator module.
"""

import os
import tempfile
import pytest
from app.core.simulator import Simulator


@pytest.fixture
def simulator():
    """Fixture to create a simulator with a temporary database file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "demo.db")
        sim = Simulator(db_path=db_path)
        yield sim
        # The temporary directory and its contents are automatically cleaned up


def test_simulator_initialization(simulator):
    """Test that the simulator initializes correctly."""
    assert simulator is not None
    # Check that the database path exists
    assert simulator.db_path.exists()


def test_get_customer_by_email(simulator):
    """Test getting a customer by email."""
    customer = simulator.get_customer_by_email("john.doe@example.com")
    assert customer is not None
    assert customer["id"] == 1
    assert customer["name"] == "John Doe"
    assert customer["email"] == "john.doe@example.com"

    # Non-existent email
    customer = simulator.get_customer_by_email("nonexistent@example.com")
    assert customer is None


def test_get_customer_by_id(simulator):
    """Test getting a customer by ID."""
    customer = simulator.get_customer_by_id(2)
    assert customer is not None
    assert customer["name"] == "Jane Smith"

    # Non-existent ID
    customer = simulator.get_customer_by_id(999)
    assert customer is None


def test_get_payment_by_transaction_id(simulator):
    """Test getting a payment by transaction ID."""
    payment = simulator.get_payment_by_transaction_id("txn_123456")
    assert payment is not None
    assert payment["amount"] == 9.99
    assert payment["status"] == "success"

    # Non-existent transaction ID
    payment = simulator.get_payment_by_transaction_id("txn_000000")
    assert payment is None


def test_get_payments_by_customer_id(simulator):
    """Test getting payments by customer ID."""
    payments = simulator.get_payments_by_customer_id(1)
    assert len(payments) == 2  # John Doe has two payments
    # Check that they are ordered by payment_date descending
    assert payments[0]["transaction_id"] == "txn_901234"  # Second payment
    assert payments[1]["transaction_id"] == "txn_123456"  # First payment

    # Customer with no payments
    payments = simulator.get_payments_by_customer_id(999)
    assert len(payments) == 0


def test_get_active_subscription_by_customer_id(simulator):
    """Test getting active subscription by customer ID."""
    # John Doe (customer 1) has an active subscription
    sub = simulator.get_active_subscription_by_customer_id(1)
    assert sub is not None
    assert sub["status"] == "active"
    assert sub["plan_name"] == "Basic"

    # Jane Smith (customer 2) has an inactive subscription
    sub = simulator.get_active_subscription_by_customer_id(2)
    assert sub is None

    # Non-existent customer
    sub = simulator.get_active_subscription_by_customer_id(999)
    assert sub is None


def test_get_subscription_by_customer_id(simulator):
    """Test getting any subscription by customer ID."""
    # Jane Smith has an inactive subscription, should still be returned
    sub = simulator.get_subscription_by_customer_id(2)
    assert sub is not None
    assert sub["status"] == "inactive"
    assert sub["plan_name"] == "Pro"

    # Non-existent customer
    sub = simulator.get_subscription_by_customer_id(999)
    assert sub is None


def test_get_plan_by_id(simulator):
    """Test getting a plan by ID."""
    plan = simulator.get_plan_by_id(2)
    assert plan is not None
    assert plan["name"] == "Pro"
    assert plan["price"] == 19.99

    # Non-existent plan ID
    plan = simulator.get_plan_by_id(999)
    assert plan is None


def test_reactivate_subscription(simulator):
    """Test reactivating a subscription."""
    # Jane Smith's subscription is inactive, should be reactivatable
    result = simulator.reactivate_subscription(2)
    assert result is True

    # Check that it is now active
    sub = simulator.get_active_subscription_by_customer_id(2)
    assert sub is not None
    assert sub["status"] == "active"

    # Try to reactivate again (should return False because it's already active)
    result = simulator.reactivate_subscription(2)
    assert result is False

    # John Doe's subscription is already active, reactivating should return False
    result = simulator.reactivate_subscription(1)
    assert result is False

    # Non-existent customer
    result = simulator.reactivate_subscription(999)
    assert result is False