"""
Tool to check the status of a payment by transaction ID.
"""

from .base import BaseTool
from ..simulator import Simulator
from app.core.config import get_settings


class CheckPaymentStatusTool(BaseTool):
    """Tool to check the status of a payment by transaction ID."""

    def __init__(self, simulator: Simulator):
        super().__init__(
            name="check_payment_status",
            description="Check the status of a payment by transaction ID. Input: transaction_id (string).",
        )
        self.simulator = simulator

    async def execute(self, transaction_id: str) -> Dict[str, Any]:
        """Check the payment status.

        Args:
            transaction_id: The transaction ID to look up.

        Returns:
            A dictionary with the payment details or an error message.
        """
        payment = self.simulator.get_payment_by_transaction_id(transaction_id)
        if payment is None:
            return {
                "success": False,
                "error": f"No payment found with transaction ID: {transaction_id}",
            }
        return {
            "success": True,
            "payment": payment,
        }

    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool's input parameters."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction ID to look up",
                    }
                },
                "required": ["transaction_id"],
            },
        }