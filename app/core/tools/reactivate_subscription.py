"""
Tool to reactivate a customer's subscription.
"""

from typing import Dict, Any
from .base import BaseTool
from ..simulator import Simulator


class ReactivateSubscriptionTool(BaseTool):
    """Tool to reactivate a customer's subscription."""

    def __init__(self, simulator: Simulator):
        super().__init__(
            name="reactivate_subscription",
            description="Reactivate the subscription for a customer. Input: customer_id (integer).",
        )
        self.simulator = simulator

    async def execute(self, customer_id: int) -> Dict[str, Any]:
        """Reactivate the subscription.

        Args:
            customer_id: The customer ID whose subscription to reactivate.

        Returns:
            A dictionary indicating success or failure.
        """
        # Check current subscription status first
        subscription = self.simulator.get_subscription_by_customer_id(customer_id)
        if subscription is None:
            return {
                "success": False,
                "error": f"No subscription found for customer ID {customer_id}.",
            }

        if subscription.get("status") == "active":
            return {
                "success": True,
                "message": f"Subscription for customer ID {customer_id} is already active.",
                "subscription": subscription,
            }

        # Subscription is inactive — attempt reactivation
        success = self.simulator.reactivate_subscription(customer_id)
        if success:
            # Fetch the updated subscription data so the verifier can validate it
            subscription = self.simulator.get_subscription_by_customer_id(customer_id)
            return {
                "success": True,
                "message": f"Subscription for customer ID {customer_id} has been reactivated.",
                "subscription": subscription,
            }
        else:
            return {
                "success": False,
                "error": f"Failed to reactivate subscription for customer ID {customer_id}. "
                         f"Check if the customer exists and has an inactive subscription.",
            }

    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool's input parameters."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The customer ID whose subscription to reactivate",
                    }
                },
                "required": ["customer_id"],
            },
        }