"""
AI provider abstraction layer.
Supports multiple AI providers with a common interface.
"""

import abc
import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any, Optional, List
import httpx
from app.core.config import get_settings


class AIProviderAbstract(abc.ABC):
    """Abstract base class for AI providers."""

    @abc.abstractmethod
    async def generate_response(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """Generate a response from the AI provider.

        Args:
            prompt: The user prompt.
            system: Optional system message.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            stream: Whether to stream the response.

        Returns:
            If stream is False, returns the complete response string.
            If stream is True, returns an async generator yielding string chunks.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def classify_intent(
        self,
        message: str,
        intents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Classify the intent of a message.

        Args:
            message: The user message.
            intents: List of possible intent labels.
            context: Optional context including business context, conversation history, etc.

        Returns:
            A dictionary with intent classification results.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def select_action(
        self,
        intent: str,
        available_tools: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Select an action to perform based on intent and context.

        Args:
            intent: The classified intent.
            available_tools: List of available tools with their schemas.
            context: Current context including conversation history, business state, etc.

        Returns:
            A dictionary representing the selected action and its parameters.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Get a structured output conforming to a JSON schema.

        Args:
            prompt: The prompt to guide the generation.
            schema: JSON schema for the expected output.
            system: Optional system message.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Returns:
            A dictionary conforming to the provided schema.
        """
        raise NotImplementedError


class MockProvider(AIProviderAbstract):
    """Mock AI provider for development and testing."""

    def __init__(self):
        self.settings = get_settings()
        self.mock_delay = 0.1  # Simulate network delay

    async def _mock_delay(self):
        """Simulate network delay."""
        await asyncio.sleep(self.mock_delay)

    async def generate_response(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """Generate a mock response."""
        await self._mock_delay()

        if stream:
            async def mock_stream():
                # Simulate streaming by yielding chunks
                yield "This is a mock response "
                yield "for testing purposes. "
                yield "It simulates streaming behavior."
            return mock_stream()
        else:
            return "This is a mock response for testing purposes."

    async def classify_intent(
        self,
        message: str,
        intents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Mock intent classification based on keywords.

        Args:
            message: The user message.
            intents: List of possible intent labels.
            context: Optional context including business context, conversation history, etc.
                (Not used in this mock implementation but kept for interface consistency).
        """
        await self._mock_delay()
        message_lower = message.lower()

        # Simple keyword matching for demo purposes
        # Check for payment-related keywords
        if any(word in message_lower for word in ["payment", "paid", "transaction", "txn"]):
            intent = "check_payment_status"
        # Check for reactivation keywords (check these before general subscription keywords)
        elif any(word in message_lower for word in ["reactivate", "renew", "restart"]):
            intent = "reactivate_subscription"
        # Check for product/plan inquiry keywords (more specific)
        elif any(word in message_lower for word in ["product", "pricing", "cost", "offer", "available", "plans"]):
            intent = "get_product_or_plan"
        # Check for subscription status keywords
        elif any(word in message_lower for word in ["subscription", "subscribed", "status"]):
            intent = "check_subscription_status"
        else:
            intent = "general_question"

        # Make sure the intent is in the list of valid intents
        if intent not in intents:
            intent = intents[0] if intents else "general_question"

        return {
            "intent": intent,
            "confidence": 0.95,
            "reasoning": f"Mock response for testing - detected keyword for {intent}"
        }

    async def select_action(
        self,
        intent: str,
        available_tools: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Mock action selection based on intent."""
        await self._mock_delay()
        # Map intent to appropriate tool
        tool_name = None
        parameters = {}

        if intent == "check_payment_status":
            tool_name = "check_payment_status"
            parameters = {"transaction_id": "txn_123456"}
        elif intent == "check_subscription_status":
            tool_name = "check_subscription_status"
            parameters = {"customer_id": 1}  # Default to customer 1 for demo
        elif intent == "reactivate_subscription":
            tool_name = "reactivate_subscription"
            parameters = {"customer_id": 2}  # Customer 2 has inactive subscription
        elif intent == "get_product_or_plan":
            tool_name = "get_product_or_plan"
            parameters = {"plan_id": 1}
        elif intent == "general_question":
            # For general questions, we don't execute a tool
            return {
                "tool_name": "general_question",
                "parameters": {},
                "reasoning": "Mock response for testing - general question"
            }
        else:
            # Fallback to first tool if intent not recognized
            if available_tools:
                tool_name = available_tools[0]["name"]
                # Provide mock parameters based on the tool name
                if tool_name == "check_payment_status":
                    parameters = {"transaction_id": "txn_123456"}
                elif tool_name == "check_subscription_status":
                    parameters = {"customer_id": 1}
                elif tool_name == "reactivate_subscription":
                    parameters = {"customer_id": 2}
                elif tool_name == "get_product_or_plan":
                    parameters = {"plan_id": 1}
                else:
                    parameters = {}
            else:
                return {
                    "tool_name": "general_question",
                    "parameters": {},
                    "reasoning": "Mock response for testing - no tools available"
                }

        # Verify the tool exists in available_tools
        if tool_name and any(tool["name"] == tool_name for tool in available_tools):
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "reasoning": f"Mock response for testing - selected {tool_name} for intent {intent}"
            }
        else:
            # Fallback to first available tool
            if available_tools:
                tool_name = available_tools[0]["name"]
                parameters = {}
                if tool_name == "check_payment_status":
                    parameters = {"transaction_id": "txn_123456"}
                elif tool_name == "check_subscription_status":
                    parameters = {"customer_id": 1}
                elif tool_name == "reactivate_subscription":
                    parameters = {"customer_id": 2}
                elif tool_name == "get_product_or_plan":
                    parameters = {"plan_id": 1}
                return {
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "reasoning": "Mock response for testing - fallback to first tool"
                }
            else:
                return {
                    "tool_name": "general_question",
                    "parameters": {},
                    "reasoning": "Mock response for testing - no tools available"
                }

    async def structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Get a mock structured output that conforms to the schema."""
        await self._mock_delay()
        # For simplicity, we'll return a dict with default values for the required fields.
        # This is not ideal but will work for testing.
        result = {}
        for prop_name, prop_schema in schema.get("properties", {}).items():
            if prop_name in schema.get("required", []):
                # Provide a default value based on the type
                prop_type = prop_schema.get("type")
                if prop_type == "string":
                    # For enum, use the first value if available
                    if "enum" in prop_schema:
                        result[prop_name] = prop_schema["enum"][0]
                    else:
                        result[prop_name] = "mock_value"
                elif prop_type == "number":
                    result[prop_name] = 0.5
                elif prop_type == "integer":
                    result[prop_name] = 0
                elif prop_type == "boolean":
                    result[prop_name] = True
                elif prop_type == "array":
                    result[prop_name] = []
                elif prop_type == "object":
                    result[prop_name] = {}
                else:
                    result[prop_name] = None
            else:
                # Optional fields, we can leave them out or set to null
                result[prop_name] = None
        return result


class AnthropicProvider(AIProviderAbstract):
    """Anthropic Claude AI provider implementation."""

    def __init__(self):
        self.settings = get_settings()
        self.provider = MockProvider()  # Always initialize fallback
        if not self.settings.anthropic_api_key or self.settings.anthropic_api_key == "your_anthropic_api_key_here":
            # In development, if the API key is not set or is the placeholder, we use mock
            self.is_mock = True
        else:
            try:
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)
                self.is_mock = False
            except ImportError:
                # Fallback to mock if anthropic package is not installed
                self.is_mock = True

    async def generate_response(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """Generate a response from Anthropic Claude."""
        if self.is_mock:
            return await self.provider.generate_response(
                prompt, system, temperature, max_tokens, stream
            )

        try:
            if stream:
                return self._stream_response(
                    prompt=prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                return await self._generate_response(
                    prompt=prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
        except Exception as e:
            # Fallback to mock on error
            return await self.provider.generate_response(
                prompt, system, temperature, max_tokens, stream
            )

    async def _generate_response(
        self,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate a non-streaming response."""
        message = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            timeout=self.settings.ai_request_timeout,
        )
        return message.content[0].text if message.content else ""

    async def _stream_response(
        self,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response."""
        async with self.client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            timeout=self.settings.ai_stream_timeout,
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    yield event.delta.text

    async def classify_intent(
        self,
        message: str,
        intents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Classify intent using Anthropic Claude with structured output."""
        if self.is_mock:
            return await self.provider.classify_intent(message, intents, context)

        try:
            # We'll use the structured output method for intent classification
            schema = {
                "type": "object",
                "properties": {
                    "intent": {"type": "string", "enum": intents},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "reasoning": {"type": "string"},
                },
                "required": ["intent", "confidence"],
            }

            # Build prompt with business context if available
            business_context = ""
            if context and "business_context" in context:
                business_context = f"\n\nBusiness Context:\n{context['business_context']}"

            prompt = f"""
            Classify the intent of the following message into one of the provided intents.
            Message: "{message}"
            Available intents: {', '.join(intents)}{business_context}
            """

            result = await self.structured_output(
                prompt=prompt,
                schema=schema,
                system="You are an expert at classifying user intents for a business customer support agent.",
                temperature=0.0,  # Deterministic for classification
            )
            return result
        except Exception as e:
            # Fallback to mock on error
            return await self.provider.classify_intent(message, intents, context)

    async def select_action(
        self,
        intent: str,
        available_tools: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Select an action using Anthropic Claude with structured output."""
        if self.is_mock:
            return await self.provider.select_action(intent, available_tools, context)

        try:
            # We'll create a schema for the action selection
            tool_names = [tool["name"] for tool in available_tools]
            schema = {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string", "enum": tool_names},
                    "parameters": {"type": "object"},
                    "reasoning": {"type": "string"},
                },
                "required": ["tool_name", "parameters"],
            }

            prompt = f"""
            Based on the intent and context, select the appropriate tool to use.
            Intent: {intent}
            Context: {context}
            Available tools: {available_tools}
            """

            result = await self.structured_output(
                prompt=prompt,
                schema=schema,
                system="You are an expert at selecting the right tool for a business customer support agent.",
                temperature=0.0,
            )
            return result
        except Exception as e:
            # Fallback to mock on error
            return await self.provider.select_action(intent, available_tools, context)

    async def structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Get a structured output from Anthropic Claude."""
        if self.is_mock:
            return await self.provider.structured_output(prompt, schema, system, temperature, max_tokens)

        try:
            # Anthropic doesn't have native JSON mode like OpenAI, so we need to prompt for JSON
            # and then parse it. We'll use the generate_response method and then parse the JSON.
            json_prompt = f"""
            {prompt}

            Respond with a JSON object that conforms to the following schema:
            {schema}

            Only output the JSON object, no additional text.
            """

            # Use generate_response to get the text response
            response_text = await self.generate_response(
                prompt=json_prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )

            # Extract the text content (response_text is a string when stream=False)
            text_content = response_text

            # Try to parse as JSON
            try:
                # Find JSON-like content in the response
                # Simple approach: look for the first '{' and last '}'
                start = text_content.find("{")
                end = text_content.rfind("}")
                if start != -1 and end != -1 and start < end:
                    json_str = text_content[start : end + 1]
                    return json.loads(json_str)
                else:
                    # If no JSON found, return an empty dict or raise an error
                    raise ValueError("No JSON object found in the response")
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON from response: {e}") from e
        except Exception as e:
            # Fallback to mock on error
            return await self.provider.structured_output(prompt, schema, system, temperature, max_tokens)


class NVIDIAProvider(AIProviderAbstract):
    """NVIDIA AI provider implementation (using NVIDIA NIMs or compatible API)."""

    def __init__(self):
        self.settings = get_settings()
        self.provider = MockProvider()  # Always initialize fallback FIRST
        if not self.settings.nvidia_api_key:
            # If API key is not set, we use mock
            self.is_mock = True
        else:
            # Initialize HTTP client for NVIDIA API
            self.client = httpx.AsyncClient(
                base_url=self.settings.nvidia_base_url,
                headers={
                    "Authorization": f"Bearer {self.settings.nvidia_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=httpx.Timeout(self.settings.ai_request_timeout)
            )
            self.is_mock = False

    async def generate_response(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """Generate a response from NVIDIA API."""
        if self.is_mock:
            return await self.provider.generate_response(
                prompt, system, temperature, max_tokens, stream
            )

        try:
            # Prepare the request payload
            payload = {
                "model": self.settings.nvidia_model,
                "messages": [],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }

            if system:
                payload["messages"].append({"role": "system", "content": system})
            payload["messages"].append({"role": "user", "content": prompt})

            if stream:
                return self._stream_response(payload)
            else:
                return await self._generate_response(payload)
        except Exception as e:
            # Fallback to mock on error
            return await self.provider.generate_response(
                prompt, system, temperature, max_tokens, stream
            )

    async def _generate_response(self, payload: Dict[str, Any]) -> str:
        """Generate a non-streaming response from NVIDIA API."""
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    async def _stream_response(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Generate a streaming response from NVIDIA API."""
        async with self.client.stream(
            "POST",
            "/chat/completions",
            json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data.strip() == "[DONE]":
                        break
                    try:
                        json_data = json.loads(data)
                        if "choices" in json_data and len(json_data["choices"]) > 0:
                            delta = json_data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        pass

    async def classify_intent(
        self,
        message: str,
        intents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Classify intent using NVIDIA API with structured output."""
        if self.is_mock:
            return await self.provider.classify_intent(message, intents, context)

        try:
            # We'll use the structured output method for intent classification
            schema = {
                "type": "object",
                "properties": {
                    "intent": {"type": "string", "enum": intents},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "reasoning": {"type": "string"},
                },
                "required": ["intent", "confidence"],
            }

            # Build prompt with business context if available
            business_context = ""
            if context and "business_context" in context:
                business_context = f"\n\nBusiness Context:\n{context['business_context']}"

            prompt = f"""
            Classify the intent of the following message into one of the provided intents.
            Message: "{message}"
            Available intents: {', '.join(intents)}{business_context}
            """

            result = await self.structured_output(
                prompt=prompt,
                schema=schema,
                system="You are an expert at classifying user intents for a business customer support agent.",
                temperature=0.0,  # Deterministic for classification
            )
            return result
        except Exception as e:
            # Fallback to mock on error
            return await self.provider.classify_intent(message, intents, context)

    async def select_action(
        self,
        intent: str,
        available_tools: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Select an action using NVIDIA API with structured output."""
        if self.is_mock:
            return await self.provider.select_action(intent, available_tools, context)

        try:
            # We'll create a schema for the action selection
            tool_names = [tool["name"] for tool in available_tools]
            schema = {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string", "enum": tool_names},
                    "parameters": {"type": "object"},
                    "reasoning": {"type": "string"},
                },
                "required": ["tool_name", "parameters"],
            }

            prompt = f"""
            Based on the intent and context, select the appropriate tool to use.
            Intent: {intent}
            Context: {context}
            Available tools: {available_tools}
            """

            result = await self.structured_output(
                prompt=prompt,
                schema=schema,
                system="You are an expert at selecting the right tool for a business customer support agent.",
                temperature=0.0,
            )
            return result
        except Exception as e:
            # Fallback to mock on error
            return await self.provider.select_action(intent, available_tools, context)

    async def structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Get a structured output from NVIDIA API."""
        if self.is_mock:
            return await self.provider.structured_output(prompt, schema, system, temperature, max_tokens)

        try:
            # Prepare the request payload for JSON mode
            payload = {
                "model": self.settings.nvidia_model,
                "messages": [],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }

            if system:
                payload["messages"].append({"role": "system", "content": system})
            payload["messages"].append({"role": "user", "content": prompt})

            # Add guidance for JSON output
            payload["messages"].append({
                "role": "system",
                "content": f"Respond with a JSON object that conforms to the following schema: {json.dumps(schema)}. Only output the JSON object, no additional text."
            })

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            result = response.json()
            text_content = result["choices"][0]["message"]["content"]

            # Try to parse as JSON
            try:
                # Find JSON-like content in the response
                start = text_content.find("{")
                end = text_content.rfind("}")
                if start != -1 and end != -1 and start < end:
                    json_str = text_content[start : end + 1]
                    return json.loads(json_str)
                else:
                    # If no JSON found, return an empty dict or raise an error
                    raise ValueError("No JSON object found in the response")
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON from response: {e}") from e
        except Exception as e:
            # Fallback to mock on error
            return await self.provider.structured_output(prompt, schema, system, temperature, max_tokens)


# Factory function to get the appropriate provider
def get_ai_provider() -> AIProviderAbstract:
    """Get an AI provider instance based on configuration."""
    settings = get_settings()
    provider_type = settings.ai_provider.lower()

    if provider_type == "anthropic":
        return AnthropicProvider()
    elif provider_type == "nvidia":
        return NVIDIAProvider()
    else:
        # Default to mock for unknown providers
        return MockProvider()
