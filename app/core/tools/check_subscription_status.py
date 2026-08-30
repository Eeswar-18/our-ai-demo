"""
Tool to check the subscription status of a customer.
"""

from typing import Dict, Any
from .base import BaseTool
from ..simulator import Simulator


class CheckSubscriptionStatusTool(BaseTool):
    """Tool to check the subscription status of a customer."""

    def __init__(self, simulator: Simulator):
        super().__init__(
            name="check_subscription_status",
            description="Check the subscription status of a customer. Input: customer_id (integer).",
        )
        self.simulator = simulator

    async def execute(self, customer_id: int) -> Dict[str, Any]:
        """Check the subscription status.

        Args:
            customer_id: The customer ID to look up.

        Returns:
            A dictionary with the subscription details or an error message.
        """
        subscription = self.simulator.get_active_subscription_by_customer_id(customer_id)
        if subscription is None:
            # Also check for any subscription (including inactive)
            any_sub = self.simulator.get_subscription_by_customer_id(customer_id)
            if any_sub is None:
                return {
                    "success": False,
                    "error": f"No subscription found for customer ID: {customer_id}",
                }
            else:
                return {
                    "success": True,
                    "subscription": any_sub,
                    "note": "Subscription is not active",
                }
        return {
            "success": True,
            "subscription": subscription,
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
                        "description": "The customer ID to look up",
                    }
                },
                "required": ["customer_id"],
            },
        }