"""
Base tool interface for the our-ai-demo V0.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with the given keyword arguments.

        Returns:
            A dictionary with the result of the tool execution.
            Should include a 'success' key indicating if the execution was successful.
        """
        raise NotImplementedError

    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool's input parameters.
        This is used by the AI provider to understand how to call the tool.
        Subclasses should override this method to provide a specific schema.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }