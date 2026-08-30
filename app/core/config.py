"""
Application configuration module.
Loads environment variables and provides settings."""

import os
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""

    def __init__(self):
        # AI Provider Selection
        self.ai_provider: str = os.getenv("AI_PROVIDER", "anthropic").lower()  # anthropic, nvidia, mock

        # Anthropic Claude
        self.anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

        # NVIDIA NIMs (or other compatible API)
        self.nvidia_api_key: str = os.getenv("NVIDIA_API_KEY", "")
        self.nvidia_base_url: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.nvidia_model: str = os.getenv("NVIDIA_MODEL", "nemotron-3-8b-chat")

        # For future providers (OpenAI, etc.)
        # self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

        # Application
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

        # Server
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))

        # Simulation
        self.simulation_seed: int = int(os.getenv("SIMULATION_SEED", "12345"))

        # Performance
        # Timeouts in seconds
        self.ai_request_timeout: float = float(os.getenv("AI_REQUEST_TIMEOUT", "30.0"))
        # Maximum time to wait for first token (streaming)
        self.ai_stream_timeout: float = float(os.getenv("AI_STREAM_TIMEOUT", "10.0"))


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()