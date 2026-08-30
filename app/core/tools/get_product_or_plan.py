"""
Tool to get a product or plan by ID.
"""

from typing import Dict, Any
from .base import BaseTool
from ..simulator import Simulator


class GetProductOrPlanTool(BaseTool):
    """Tool to get a product or plan by ID."""

    def __init__(self, simulator: Simulator):
        super().__init__(
            name="get_product_or_plan",
            description="Get a product or plan by ID. Input: plan_id (integer).",
        )
        self.simulator = simulator

    async def execute(self, plan_id: int) -> Dict[str, Any]:
        """Get the plan details.

        Args:
            plan_id: The plan ID to look up.

        Returns:
            A dictionary with the plan details or an error message.
        """
        plan = self.simulator.get_plan_by_id(plan_id)
        if plan is None:
            return {
                "success": False,
                "error": f"No plan found with ID: {plan_id}",
            }
        return {
            "success": True,
            "plan": plan,
        }

    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool's input parameters."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "integer",
                        "description": "The plan ID to look up",
                    }
                },
                "required": ["plan_id"],
            },
        }