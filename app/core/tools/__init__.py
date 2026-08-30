"""
Tool registry for the our-ai-demo V0.
"""

from .check_payment_status import CheckPaymentStatusTool
from .check_subscription_status import CheckSubscriptionStatusTool
from .reactivate_subscription import ReactivateSubscriptionTool
from .get_product_or_plan import GetProductOrPlanTool
from .escalate import EscalateTool

# Export the tools for easy import
__all__ = [
    "CheckPaymentStatusTool",
    "CheckSubscriptionStatusTool",
    "ReactivateSubscriptionTool",
    "GetProductOrPlanTool",
    "EscalateTool",
]


def get_tool_registry(simulator: "Simulator"):
    """Create and return a registry of available tools.
    Args:
        simulator: The simulator instance to pass to the tools.
    Returns:
        A dictionary mapping tool names to tool instances.
    """
    return {
        "check_payment_status": CheckPaymentStatusTool(simulator),
        "check_subscription_status": CheckSubscriptionStatusTool(simulator),
        "reactivate_subscription": ReactivateSubscriptionTool(simulator),
        "get_product_or_plan": GetProductOrPlanTool(simulator),
        "escalate": EscalateTool(),
    }