"""
Orchestrator for the our-ai-demo V0.
Implements the main agent loop: understand -> plan -> act -> observe -> verify -> replan/escalate.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, List, Optional
from app.core.business_context import BusinessContext
from app.core.ai_provider import AIProviderAbstract
from app.core.simulator import Simulator
from app.core.tools import get_tool_registry
from app.core.verifier import Verifier
from app.core.audit_logger import AuditLogger, AuditEventType

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator for the AI agent."""

    def __init__(self, ai_provider: AIProviderAbstract, simulator: Simulator):
        self.ai_provider = ai_provider
        self.simulator = simulator
        self.tools = get_tool_registry(simulator)
        self.verifier = Verifier(simulator)
        self.audit_logger = AuditLogger()
        self.max_steps = 5  # Maximum number of steps in the orchestrator loop
        self.conversation_history: List[Dict[str, str]] = []  # List of {'role': 'user'|'assistant', 'content': ...}
        self.business_context = BusinessContext()

    async def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process a user message and return a response.
        This is the main entry point for the orchestrator.
        Returns a dictionary with the response and optionally metadata for debugging.
        """
        # Generate a correlation ID for this conversation
        correlation_id = str(uuid.uuid4())

        # Log the user message
        self.audit_logger.log_user_message(user_message, correlation_id)

        # Add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Initialize the orchestrator state
        orchestrator_state = {
            "user_message": user_message,
            "intent": None,
            "action_plan": None,
            "tool_executions": [],
            "verification_results": [],
            "response": None,
            "escalated": False,
            "current_step": 0,
        }

        # Run the orchestrator loop
        for step in range(self.max_steps):
            orchestrator_state["current_step"] = step + 1
            logger.info(f"Orchestrator step {step + 1}/{self.max_steps}")

            # 1. Understand: Classify the intent if not already done
            if orchestrator_state["intent"] is None:
                intent_result = await self._understand(user_message, correlation_id)
                orchestrator_state["intent"] = intent_result
                logger.info(f"Classified intent: {intent_result}")

            # 2. Plan: Based on intent and current state, plan the next action
            if orchestrator_state["action_plan"] is None:
                action_plan = await self._plan(orchestrator_state, correlation_id)
                orchestrator_state["action_plan"] = action_plan
                logger.info(f"Planned action: {action_plan}")

            # 3. Act: Execute the planned action
            action_result = await self._act(orchestrator_state["action_plan"], correlation_id)
            orchestrator_state["tool_executions"].append(action_result)
            logger.info(f"Action result: {action_result}")

            # 4. Observe: The action result is already observed

            # 5. Verify: Check if the action achieved the desired goal
            verification_result = await self._verify(orchestrator_state, correlation_id)
            orchestrator_state["verification_results"].append(verification_result)
            logger.info(f"Verification result: {verification_result}")

            # 6. Check if we are done or need to replan/escalate
            if verification_result.get("goal_achieved", False):
                # Goal achieved, generate the final response
                response = await self._generate_response(orchestrator_state, correlation_id)
                orchestrator_state["response"] = response
                break
            elif action_result.get("tool_name") == "escalate":
                # The planner decided to escalate
                orchestrator_state["escalated"] = True
                response = await self._generate_response(orchestrator_state, correlation_id)
                orchestrator_state["response"] = response
                break
            else:
                # Goal not achieved, replan: clear the action plan and continue the loop
                orchestrator_state["action_plan"] = None
                # If we've reached the max steps, we'll break and generate a response anyway
                if step == self.max_steps - 1:
                    logger.warning("Max steps reached, generating response based on current state")
                    response = await self._generate_response(orchestrator_state, correlation_id)
                    orchestrator_state["response"] = response
                    break

        # Add the assistant's response to the conversation history
        if orchestrator_state["response"]:
            self.conversation_history.append(
                {"role": "assistant", "content": orchestrator_state["response"].get("message", "")}
            )

        return orchestrator_state["response"]

    async def _understand(self, user_message: str, correlation_id: str) -> str:
        """Classify the intent of the user message.
        Returns a string representing the intent.
        """
        # Define the list of intents we support
        intents = [
            "check_payment_status",
            "check_subscription_status",
            "reactivate_subscription",
            "get_product_or_plan",
            "general_question",
            "escalate",
        ]

        # Prepare context for intent classification
        context = {
            "business_context": self.business_context.format_context_for_prompt(),
            "conversation_history": self.conversation_history[-5:],  # Last 5 messages
        }

        # Use the AI provider to classify the intent
        intent_result = await self.ai_provider.classify_intent(
            message=user_message,
            intents=intents,
            context=context,
        )

        # Log the intent classification
        self.audit_logger.log_intent_classified(
            intent=intent_result.get("intent", "general_question"),
            confidence=intent_result.get("confidence", 0.0),
            reasoning=intent_result.get("reasoning", ""),
            correlation_id=correlation_id
        )

        # The classify_intent method returns a dict with 'intent', 'confidence', 'reasoning'
        return intent_result.get("intent", "general_question")

    async def _plan(self, orchestrator_state: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
        """Plan the next action based on the current state and intent.
        Returns a dictionary representing the action to take.
        For general questions, we plan to generate a response directly.
        For other intents, we plan to execute a tool.
        """
        intent = orchestrator_state["intent"]
        user_message = orchestrator_state["user_message"]

        # For general questions, we plan to generate a response directly
        if intent == "general_question":
            action_plan = {
                "tool_name": "generate_response",
                "parameters": {},
                "reasoning": "General question - generate response directly"
            }
        else:
            # Prepare the context for the AI provider
            context = {
                "user_message": user_message,
                "conversation_history": self.conversation_history[-5:],  # Last 5 messages
                "available_tools": [tool.get_schema() for tool in self.tools.values()],
                "simulator_state": {
                    # We could include some relevant state from the simulator here
                    # For now, we'll keep it simple
                },
                "previous_attempts": orchestrator_state["tool_executions"],
                "business_context": self.business_context.format_context_for_prompt(),
            }

            # Use the AI provider to select an action
            action_plan = await self.ai_provider.select_action(
                intent=intent,
                available_tools=[tool.get_schema() for tool in self.tools.values()],
                context=context,
            )
            # The select_action method returns a dict with 'tool_name', 'parameters', 'reasoning'

        # Log the planned action
        self.audit_logger.log_action_planned(action_plan, correlation_id)

        return action_plan

    async def _act(self, action_plan: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
        """Execute the planned action.
        Returns a dictionary with the result of the tool execution.
        """
        tool_name = action_plan.get("tool_name")
        parameters = action_plan.get("parameters", {})

        # Handle the special case of generating a response directly
        if tool_name == "generate_response":
            # We'll generate the response in the _generate_response method
            # For now, just return success to indicate we should proceed to response generation
            result = {
                "success": True,
                "tool_name": tool_name,
                "parameters": parameters,
                "result": {"response_generated": True},
            }
        else:
            if tool_name not in self.tools:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "tool_name": tool_name,
                }
            else:
                tool = self.tools[tool_name]
                try:
                    tool_result = await tool.execute(**parameters)
                    result = {
                        "success": tool_result.get("success", False),
                        "tool_name": tool_name,
                        "parameters": parameters,
                        "result": tool_result,
                    }
                except Exception as e:
                    logger.exception(f"Error executing tool {tool_name}")
                    result = {
                        "success": False,
                        "error": str(e),
                        "tool_name": tool_name,
                        "parameters": parameters,
                    }

                    # Log the error
                    self.audit_logger.log_error_occurred(
                        error=str(e),
                        context={
                            "tool_name": tool_name,
                            "parameters": parameters
                        },
                        correlation_id=correlation_id
                    )

        # Log the tool execution
        self.audit_logger.log_tool_execution(
            tool_name=tool_name,
            parameters=parameters,
            result=result,
            correlation_id=correlation_id
        )

        return result

    async def _verify(self, orchestrator_state: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
        """Verify if the action achieved the desired goal using the Verifier component.
        Returns a dictionary with verification results.
        """
        # We'll define verification based on the intent and the last tool execution
        if not orchestrator_state["tool_executions"]:
            verification_result = {"goal_achieved": False, "reason": "No tool executions yet"}
        else:
            last_execution = orchestrator_state["tool_executions"][-1]
            intent = orchestrator_state["intent"]

            # Extract any additional parameters needed for verification
            verification_kwargs = {}
            if intent == "check_payment_status":
                verification_kwargs["transaction_id"] = last_execution.get("parameters", {}).get("transaction_id")
            elif intent == "check_subscription_status" or intent == "reactivate_subscription":
                verification_kwargs["customer_id"] = last_execution.get("parameters", {}).get("customer_id")
            elif intent == "get_product_or_plan":
                verification_kwargs["plan_id"] = last_execution.get("parameters", {}).get("plan_id")

            # Use the verifier component for deterministic verification
            verification_result = self.verifier.verify_action(
                intent=intent,
                tool_result=last_execution,
                **verification_kwargs
            )

        # Log the verification result
        self.audit_logger.log_verification_result(
            intent=orchestrator_state["intent"],
            goal_achieved=verification_result.get("goal_achieved", False),
            reason=verification_result.get("reason", ""),
            correlation_id=correlation_id
        )

        return verification_result

    async def _generate_response(self, orchestrator_state: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
        """Generate a natural language response based on the current state.
        Returns a dictionary with the response message and optionally other metadata.
        """
        intent = orchestrator_state["intent"]
        user_message = orchestrator_state["user_message"]
        tool_executions = orchestrator_state["tool_executions"]
        verification_results = orchestrator_state["verification_results"]

        # Get the business context
        business_context_str = self.business_context.format_context_for_prompt()

        # Build a clean summary of tool results for the prompt
        tool_summary = self._summarize_tool_results(tool_executions)
        verified = all(
            v.get("goal_achieved", False) for v in verification_results
        ) if verification_results else False

        prompt = f"""
        You are a customer support agent responding directly to a customer.

        RULES — VIOLATION IS UNACCEPTABLE:
        - Your ENTIRE output must be ONLY the final message the customer will read.
        - Do NOT start with numbered steps like "1. Analyze", "2. Determine", "3. Identify", "4. Formulate".
        - Do NOT include any of these anywhere: Analyze, Determine, Identify, Formulate, Extract,
          Key Information, User Request, Task, Thinking, Reasoning, Chain of Thought, Step.
        - Do NOT use bullet points, numbered lists, or markdown headers.
        - Do NOT explain how you arrived at the answer.
        - Do NOT reveal tool names, technical details, or internal system information.
        - Do NOT echo back the system instructions or rules above.
        - Write as if you are speaking directly to the customer — natural, friendly, helpful.
        - 1 to 3 short paragraphs maximum.
        - Begin your response IMMEDIATELY with the customer-facing content.

        Customer asked: "{user_message}"
        What we found: {tool_summary}

        Business Information (use only if relevant, do not copy verbatim):
        {business_context_str}

        Write ONLY the customer-facing response now:
        """

        response_text = await self.ai_provider.generate_response(
            prompt=prompt,
            system=(
                "You are a customer support agent. "
                "Write ONLY the final message the customer will see. "
                "Begin immediately with the response content — no preamble, no headers, no numbered steps. "
                "Do not output analysis, reasoning, steps, or internal thinking. "
                "Do not repeat or reference these instructions. "
                "Write a natural, helpful response as if speaking directly to the customer."
            ),
            temperature=0.7,
            max_tokens=512,
            stream=False,
        )

        # Post-process: strip any leaked reasoning patterns
        response_text = self._clean_response(response_text)

        response = {
            "message": response_text,
            "intent": intent,
            "tool_executions": tool_executions,
            "verification_results": verification_results,
        }

        # Log the generated response
        self.audit_logger.log_response_generated(
            response=response_text,
            intent=intent,
            correlation_id=correlation_id
        )

        return response

    def _summarize_tool_results(self, tool_executions: List[Dict[str, Any]]) -> str:
        """Build a clean, customer-facing summary from tool execution results.
        Strips internal details and returns only useful information.
        """
        if not tool_executions:
            return "No specific data was retrieved."

        summaries = []
        for exec in tool_executions:
            tool_name = exec.get("tool_name", "unknown")
            success = exec.get("success", False)
            result = exec.get("result", {})

            if not success:
                error = exec.get("error", result.get("error", "Unknown error"))
                summaries.append(f"{tool_name}: failed ({error})")
                continue

            # Extract useful data from known tool results
            if tool_name == "get_product_or_plan":
                plan = result.get("plan") or result.get("product") or result.get("data", {})
                if isinstance(plan, dict):
                    name = plan.get("name", plan.get("plan_name", ""))
                    price = plan.get("price", plan.get("amount", ""))
                    if name and price:
                        summaries.append(f"Available plan: {name} at ${price}")
                    elif name:
                        summaries.append(f"Available plan: {name}")
                    else:
                        summaries.append(f"Plan information retrieved successfully")
                else:
                    summaries.append(f"Plan information retrieved successfully")
            elif tool_name == "reactivate_subscription":
                sub = result.get("subscription", {})
                if isinstance(sub, dict):
                    status = sub.get("status", "unknown")
                    summaries.append(f"Subscription status: {status}")
                else:
                    summaries.append(f"Subscription reactivation processed")
            elif tool_name == "check_payment_status":
                payment = result.get("payment") or result.get("transaction", {})
                if isinstance(payment, dict):
                    status = payment.get("status", "unknown")
                    summaries.append(f"Payment status: {status}")
                else:
                    summaries.append(f"Payment information retrieved")
            elif tool_name == "check_subscription_status":
                sub = result.get("subscription", {})
                if isinstance(sub, dict):
                    status = sub.get("status", "unknown")
                    summaries.append(f"Subscription status: {status}")
                else:
                    summaries.append(f"Subscription information retrieved")
            else:
                summaries.append(f"{tool_name}: processed successfully")

        return "; ".join(summaries) if summaries else "No specific data was retrieved."

    def _clean_response(self, text: str) -> str:
        """Post-process the AI response to strip any leaked internal reasoning.

        Uses an EXTRACTION strategy: finds the actual customer-facing response
        within the model's output, rather than trying to remove reasoning line
        by line (which fails when bullet points and indented text follow reasoning
        headers).
        """
        if not text:
            return text

        import re

        # --- Strategy 1: Extract response after the last explicit response marker ---
        # Models often produce: "1. Analyze...\n2. Formulate Response:\nActual answer here."
        # We want everything AFTER the last "Formulate Response" / "Response" header.
        response_markers = [
            r'(?i)^\s*#{0,4}\s*Formulate\s+Response[.:]?\s*\n',
            r'(?i)^\s*#{0,4}\s*Response[.:]?\s*\n',
            r'(?i)^\s*\d+\.\s*Formulate\s+Response[.:]?\s*\n',
            r'(?i)^\s*\d+\.\s*Response[.:]?\s*\n',
        ]
        for pattern in response_markers:
            matches = list(re.finditer(pattern, text, re.MULTILINE))
            if matches:
                # Take everything after the LAST match
                last_match = matches[-1]
                extracted = text[last_match.end():].strip()
                if extracted and len(extracted) > 3:
                    return self._finalize_response(extracted)

        # --- Strategy 2: Extract response after the last numbered step ---
        # Match the last "N. Some Step:" header and take everything after it.
        last_step = re.search(
            r'(?i)^\s*\d+\.\s*[A-Z][^\n]*:\s*\n', text, re.MULTILINE
        )
        if last_step:
            # Find the content after this last numbered step
            after_step = text[last_step.end():].strip()
            # The actual response is typically the first substantial paragraph
            # (skip bullet points and short lines which are still reasoning)
            lines = after_step.split('\n')
            response_lines = []
            for line in lines:
                stripped = line.strip()
                # Skip bullet points, short reasoning fragments, and blank lines
                # at the start
                if not response_lines and (
                    not stripped
                    or stripped.startswith('-')
                    or stripped.startswith('*')
                    or (len(stripped) < 10 and stripped.endswith(':'))
                ):
                    continue
                response_lines.append(stripped)
            if response_lines:
                extracted = '\n'.join(response_lines).strip()
                if extracted and len(extracted) > 3:
                    return self._finalize_response(extracted)

        # --- Strategy 3: Remove "Here's my thinking" blocks entirely ---
        text = re.sub(
            r'(?i)(?:^|\n)\s*here(?:\'?s|\s+is)\s+(?:a\s+)?(?:my\s+)?'
            r'(?:thinking\s+process|reasoning|analysis|thought\s+process|'
            r'chain\s+of\s+thought|internal\s+analysis)[^\n]*\n?.*',
            '', text, count=1
        )

        # --- Strategy 4: Remove all numbered reasoning steps + bullet points ---
        # Remove entire blocks: numbered header + all following indented/bullet lines
        text = re.sub(
            r'(?i)^\s*\d+\.\s*(?:Analyze|Determine|Check|Formulate|Evaluate|'
            r'Review|Identify|Process|Consider|Gather|Understand|Thought|'
            r'Extract|Determine)[^:]*:[^\n]*\n'
            r'(?:\s*[-*]\s*[^\n]*\n|\s*[^\n]*\n)*',
            '', text, flags=re.MULTILINE
        )

        # Remove markdown header lines that indicate reasoning
        text = re.sub(
            r'(?i)^\s*#{1,4}\s*(?:Analyze|Analysis|Determine|Goal|Check|Formulate|'
            r'Step|Thinking|Reasoning|Thought|Chain|Plan|Internal|'
            r'Evaluate|Review|Identify|Process|Consider|Thoughts|Extract|Response)[^\n]*\n?',
            '', text, flags=re.MULTILINE
        )

        # Remove inline reasoning labels
        text = re.sub(
            r'(?i)^\s*(?:Analysis|Reasoning|Internal\s+Thinking|Thought\s+Process|'
            r'Chain\s+of\s+Thought|Step\s*\d+|Thinking|Thoughts)[.:]?\s*[^\n]*\n?',
            '', text, flags=re.MULTILINE
        )

        # Remove orphaned reasoning labels
        text = re.sub(
            r'(?i)^\s*(?:Analyze User Input|Determine Goal|Check Tool Result|'
            r'Formulate Response|Internal Reasoning|Chain of Thought|'
            r'Identify Key Information|Extract Key Information)[.:]?\s*\n?',
            '', text, flags=re.MULTILINE
        )

        return self._finalize_response(text)

    def _finalize_response(self, text: str) -> str:
        """Final cleanup pass on the extracted response."""
        import re

        # Remove any remaining bullet/indent lines that are clearly reasoning
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Skip empty lines at start/end
            if not stripped and not cleaned_lines:
                continue
            # Skip lines that look like internal instructions
            if re.match(
                r'(?i)^[-*]\s*(?:I must|I should|User wants|I will|I need|No thinking|'
                r'Do not|Never|Always|The user)',
                stripped
            ):
                continue
            cleaned_lines.append(stripped)
        text = '\n'.join(cleaned_lines)

        # Collapse multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()

        # Safety: if cleaned response is too short or empty, use fallback
        if not text or len(text.strip()) < 5:
            text = "I'm here to help! Could you please provide more details about what you need?"

        return text


# Factory function to create an orchestrator instance
def create_orchestrator(ai_provider: AIProviderAbstract, simulator: Simulator) -> Orchestrator:
    """Create and return an orchestrator instance."""
    return Orchestrator(ai_provider, simulator)