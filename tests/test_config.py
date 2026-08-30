"""
Test configuration module.
"""

import os
from app.core.config import Settings, get_settings


def test_settings_loads():
    """Test that settings can be loaded and have expected defaults."""
    # Set environment variables for a clean test
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["HOST"] = "127.0.0.1"
    os.environ["PORT"] = "9000"
    os.environ["SIMULATION_SEED"] = "999"
    os.environ["AI_REQUEST_TIMEOUT"] = "5.0"
    os.environ["AI_STREAM_TIMEOUT"] = "2.0"

    settings = Settings()
    assert settings.anthropic_api_key == "test-key"
    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"
    assert settings.host == "127.0.0.1"
    assert settings.port == 9000
    assert settings.simulation_seed == 999
    assert settings.ai_request_timeout == 5.0
    assert settings.ai_stream_timeout == 2.0

    # Clean up
    for key in [
        "ANTHROPIC_API_KEY",
        "ENVIRONMENT",
        "LOG_LEVEL",
        "HOST",
        "PORT",
        "SIMULATION_SEED",
        "AI_REQUEST_TIMEOUT",
        "AI_STREAM_TIMEOUT",
    ]:
        os.environ.pop(key, None)


def test_get_settings_cached():
    """Test that get_settings returns a cached instance."""
    # Set a dummy key
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
    os.environ.pop("ANTHROPIC_API_KEY", None)
    # Clear the cache for the next test
    get_settings.cache_clear()