"""
Tool to escalate to a human agent.
"""

from .base import BaseTool
from typing import Dict, Any


class EscalateTool(BaseTool):
    """Tool to escalate to a human agent."""

    def __init__(self):
        super().__init__(
            name="escalate",
            description="Escalate the issue to a human agent. No input required.",
        )

    async def execute(self) -> Dict[str, Any]:
        """Escalate the issue.
        Returns:
            A dictionary indicating success.
        """
        return {
            "success": True,
        }

    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool's input parameters."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }