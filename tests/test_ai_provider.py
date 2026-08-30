"""
Test AI provider module.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.core.ai_provider import AnthropicProvider, AIProviderAbstract, get_ai_provider
from app.core.config import get_settings


@pytest.fixture
def mock_anthropic_client():
    """Fixture to mock the AsyncAnthropic client."""
    with patch("anthropic.AsyncAnthropic") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def provider(mock_anthropic_client):
    """Fixture to create an AnthropicProvider with a mocked client."""
    # We need to set the API key in the environment for the provider to initialize
    import os

    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    # Reload the settings to pick up the new environment variable
    from app.core.config import get_settings

    get_settings.cache_clear()
    provider = AnthropicProvider()
    yield provider
    # Clean up
    os.environ.pop("ANTHROPIC_API_KEY", None)
    get_settings.cache_clear()


def test_provider_is_abstract():
    """Test that AIProviderAbstract is an abstract base class."""
    with pytest.raises(TypeError):
        AIProviderAbstract()


def test_provider_instantiation(provider):
    """Test that AnthropicProvider can be instantiated."""
    assert isinstance(provider, AnthropicProvider)
    assert isinstance(provider, AIProviderAbstract)


def test_get_ai_provider(mock_anthropic_client):
    """Test the factory function."""
    import os

    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    os.environ["AI_PROVIDER"] = "anthropic"
    get_settings.cache_clear()
    provider = get_ai_provider()
    assert isinstance(provider, AnthropicProvider)
    os.environ.pop("ANTHROPIC_API_KEY", None)
    os.environ.pop("AI_PROVIDER", None)
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_generate_response_non_streaming(provider, mock_anthropic_client):
    """Test non-streaming response generation."""
    # Mock the response from Anthropic
    mock_response = Mock()
    mock_response.content = [Mock(text="Hello, world!")]
    mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

    result = await provider.generate_response(
        prompt="Hello",
        stream=False,
    )

    assert result == "Hello, world!"
    mock_anthropic_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_response_streaming(provider, mock_anthropic_client):
    """Test streaming response generation."""
    # Mock the streaming response
    async def mock_stream():
        yield Mock(type="content_block_delta", delta=Mock(text="Hello"))
        yield Mock(type="content_block_delta", delta=Mock(text=" "))
        yield Mock(type="content_block_delta", delta=Mock(text="world!"))

    # Create a mock async context manager
    mock_stream_context = AsyncMock()
    mock_stream_context.__aenter__.return_value = mock_stream()
    mock_anthropic_client.messages.stream = Mock(return_value=mock_stream_context)

    # Call the method with stream=True
    result = await provider.generate_response(prompt="Hello", stream=True)

    # The result should be an async generator
    chunks = []
    async for chunk in result:
        chunks.append(chunk)

    assert chunks == ["Hello", " ", "world!"]


@pytest.mark.asyncio
async def test_structured_output(provider, mock_anthropic_client):
    """Test structured output generation."""
    # Mock the response from Anthropic
    mock_response = Mock()
    mock_response.content = [Mock(text='{"key": "value"}')]
    mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

    schema = {
        "type": "object",
        "properties": {"key": {"type": "string"}},
        "required": ["key"],
    }

    result = await provider.structured_output(
        prompt="Test prompt",
        schema=schema,
    )

    assert result == {"key": "value"}
    mock_anthropic_client.messages.create.assert_called_once()


# Additional tests for classify_intent and select_action can be added similarly