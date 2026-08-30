"""
Verifier component for the our-ai-demo V0.
Provides deterministic state verification to ensure AI never claims success
without actual business state changes.
"""

from typing import Dict, Any, Optional
from app.core.simulator import Simulator
from app.core.business_context import BusinessContext
import logging

logger = logging.getLogger(__name__)


class Verifier:
    """Deterministic verifier for checking if tool actions achieved desired state changes."""

    def __init__(self, simulator: Simulator):
        self.simulator = simulator

    def verify_payment_status(self, transaction_id: str, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that payment status check was successful and returned correct data.

        Args:
            transaction_id: The transaction ID that was checked
            tool_result: The result from the check_payment_status tool execution

        Returns:
            Dictionary with verification results: {'goal_achieved': bool, 'reason': str}
        """
        # First check if the tool reported success
        if not tool_result.get("success", False):
            return {
                "goal_achieved": False,
                "reason": f"Tool failed: {tool_result.get('error', 'Unknown error')}"
            }

        # Check if payment data was returned
        payment_data = tool_result.get("result", {}).get("payment")
        if not payment_data:
            return {
                "goal_achieved": False,
                "reason": "Tool succeeded but returned no payment data"
            }

        # Verify the payment data matches what's in the simulator
        actual_payment = self.simulator.get_payment_by_transaction_id(transaction_id)
        if actual_payment is None:
            return {
                "goal_achieved": False,
                "reason": f"No payment found in simulator for transaction ID: {transaction_id}"
            }

        # Compare key fields to ensure consistency
        if (payment_data.get("id") == actual_payment.get("id") and
            payment_data.get("transaction_id") == actual_payment.get("transaction_id") and
            payment_data.get("amount") == actual_payment.get("amount") and
            payment_data.get("status") == actual_payment.get("status")):
            return {
                "goal_achieved": True,
                "reason": "Payment status verified successfully"
            }
        else:
            return {
                "goal_achieved": False,
                "reason": "Payment data mismatch between tool result and simulator"
            }

    def verify_subscription_status(self, customer_id: int, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that subscription status check was successful and returned correct data.

        Args:
            customer_id: The customer ID whose subscription was checked
            tool_result: The result from the check_subscription_status tool execution

        Returns:
            Dictionary with verification results: {'goal_achieved': bool, 'reason': str}
        """
        # First check if the tool reported success
        if not tool_result.get("success", False):
            return {
                "goal_achieved": False,
                "reason": f"Tool failed: {tool_result.get('error', 'Unknown error')}"
            }

        # Check if subscription data was returned
        subscription_data = tool_result.get("result", {}).get("subscription")
        if not subscription_data:
            return {
                "goal_achieved": False,
                "reason": "Tool succeeded but returned no subscription data"
            }

        # Verify the subscription data matches what's in the simulator
        actual_subscription = self.simulator.get_subscription_by_customer_id(customer_id)
        if actual_subscription is None:
            return {
                "goal_achieved": False,
                "reason": f"No subscription found in simulator for customer ID: {customer_id}"
            }

        # Compare key fields to ensure consistency
        if (subscription_data.get("id") == actual_subscription.get("id") and
            subscription_data.get("customer_id") == actual_subscription.get("customer_id") and
            subscription_data.get("plan_id") == actual_subscription.get("plan_id") and
            subscription_data.get("status") == actual_subscription.get("status")):
            return {
                "goal_achieved": True,
                "reason": "Subscription status verified successfully"
            }
        else:
            return {
                "goal_achieved": False,
                "reason": "Subscription data mismatch between tool result and simulator"
            }

    def verify_reactivate_subscription(self, customer_id: int, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that subscription reactivation was successful.

        Args:
            customer_id: The customer ID whose subscription was reactivated
            tool_result: The result from the reactivate_subscription tool execution

        Returns:
            Dictionary with verification results: {'goal_achieved': bool, 'reason': str}
        """
        # First check if the tool reported success
        if not tool_result.get("success", False):
            return {
                "goal_achieved": False,
                "reason": f"Tool failed: {tool_result.get('error', 'Unknown error')}"
            }

        # Check what the tool returned
        subscription_data = tool_result.get("result", {}).get("subscription")
        if not subscription_data:
            return {
                "goal_achieved": False,
                "reason": "Tool succeeded but returned no subscription data"
            }

        # Verify the subscription is now active in the simulator
        actual_subscription = self.simulator.get_subscription_by_customer_id(customer_id)
        if actual_subscription is None:
            return {
                "goal_achieved": False,
                "reason": f"No subscription found in simulator for customer ID: {customer_id}"
            }

        # Check if the subscription is now active
        if actual_subscription.get("status") == "active":
            return {
                "goal_achieved": True,
                "reason": "Subscription reactivation verified successfully"
            }
        else:
            return {
                "goal_achieved": False,
                "reason": f"Subscription is not active (status: {actual_subscription.get('status')})"
            }

    def verify_get_product_or_plan(self, plan_id: int, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that plan retrieval was successful and returned correct data.

        Args:
            plan_id: The plan ID that was retrieved
            tool_result: The result from the get_product_or_plan tool execution

        Returns:
            Dictionary with verification results: {'goal_achieved': bool, 'reason': str}
        """
        # First check if the tool reported success
        if not tool_result.get("success", False):
            return {
                "goal_achieved": False,
                "reason": f"Tool failed: {tool_result.get('error', 'Unknown error')}"
            }

        # Check if plan data was returned
        plan_data = tool_result.get("result", {}).get("plan")
        if not plan_data:
            return {
                "goal_achieved": False,
                "reason": "Tool succeeded but returned no plan data"
            }

        # Verify the plan data matches what's in the simulator
        actual_plan = self.simulator.get_plan_by_id(plan_id)
        if actual_plan is None:
            return {
                "goal_achieved": False,
                "reason": f"No plan found in simulator for plan ID: {plan_id}"
            }

        # Compare key fields to ensure consistency
        if (plan_data.get("id") == actual_plan.get("id") and
            plan_data.get("name") == actual_plan.get("name") and
            plan_data.get("price") == actual_plan.get("price") and
            plan_data.get("features") == actual_plan.get("features")):
            return {
                "goal_achieved": True,
                "reason": "Plan details verified successfully"
            }
        else:
            return {
                "goal_achieved": False,
                "reason": "Plan data mismatch between tool result and simulator"
            }

    def verify_general_question(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that a general question response was generated.

        Args:
            tool_result: The result from the generate_response tool execution

        Returns:
            Dictionary with verification results: {'goal_achieved': bool, 'reason': str}
        """
        # First check if the tool reported success
        if not tool_result.get("success", False):
            return {
                "goal_achieved": False,
                "reason": f"Tool failed: {tool_result.get('error', 'Unknown error')}"
            }

        # For general questions, we consider it successful if the tool indicated a response was generated
        result_data = tool_result.get("result", {})
        if not result_data.get("response_generated", False):
            return {
                "goal_achieved": False,
                "reason": "Failed to generate response for general question"
            }

        return {
            "goal_achieved": True,
            "reason": "General question response generated successfully"
        }

    def verify_escalate(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that escalation was processed.

        Args:
            tool_result: The result from the escalate tool execution

        Returns:
            Dictionary with verification results: {'goal_achieved': bool, 'reason': str}
        """
        # First check if the tool reported success
        if not tool_result.get("success", False):
            return {
                "goal_achieved": False,
                "reason": f"Tool failed: {tool_result.get('error', 'Unknown error')}"
            }

        return {
            "goal_achieved": True,
            "reason": "Escalation processed successfully"
        }

    def verify_action(self, intent: str, tool_result: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Main verification method that routes to the appropriate verifier based on intent.

        Args:
            intent: The intent being verified (check_payment_status, check_subscription_status, etc.)
            tool_result: The result from the tool execution
            **kwargs: Additional parameters needed for specific verifiers (transaction_id, customer_id, etc.)

        Returns:
            Dictionary with verification results: {'goal_achieved': bool, 'reason': str}
        """
        logger.debug(f"Verifying action for intent: {intent}")

        if intent == "check_payment_status":
            transaction_id = kwargs.get("transaction_id")
            if not transaction_id:
                return {"goal_achieved": False, "reason": "Missing transaction_id for payment verification"}
            return self.verify_payment_status(transaction_id, tool_result)

        elif intent == "check_subscription_status":
            customer_id = kwargs.get("customer_id")
            if not customer_id:
                return {"goal_achieved": False, "reason": "Missing customer_id for subscription verification"}
            return self.verify_subscription_status(customer_id, tool_result)

        elif intent == "reactivate_subscription":
            customer_id = kwargs.get("customer_id")
            if not customer_id:
                return {"goal_achieved": False, "reason": "Missing customer_id for reactivation verification"}
            return self.verify_reactivate_subscription(customer_id, tool_result)

        elif intent == "get_product_or_plan":
            plan_id = kwargs.get("plan_id")
            if not plan_id:
                return {"goal_achieved": False, "reason": "Missing plan_id for product/plan verification"}
            return self.verify_get_product_or_plan(plan_id, tool_result)

        elif intent == "general_question":
            return self.verify_general_question(tool_result)

        elif intent == "escalate":
            return self.verify_escalate(tool_result)

        else:
            return {
                "goal_achieved": False,
                "reason": f"Unknown intent for verification: {intent}"
            }