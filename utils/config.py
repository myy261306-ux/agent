"""
Configuration Management Module
Loads and manages all environment variables and configuration settings
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class Config:
    """Central configuration manager for the agent system"""

    # LLM Provider Configuration
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")

    # System Configuration
    PROJECTS_DIR: str = os.getenv("PROJECTS_DIR", "~/agent-projects")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_VERBOSE_MODE: bool = os.getenv("ENABLE_VERBOSE_MODE", "False").lower() == "true"
    MAX_CONCURRENT_AGENTS: int = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "60"))

    # LLM Models - Using currently supported models
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENROUTER_MODEL: str = "meta-llama/llama-3-70b-instruct"

    # Rate Limiting
    GROQ_RATE_LIMIT: int = 30  # requests per minute
    OPENROUTER_RATE_LIMIT: int = 20  # requests per minute

    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0  # seconds
    RETRY_BACKOFF: float = 2.0  # exponential backoff multiplier

    @classmethod
    def validate(cls) -> None:
        """Validate that configuration is valid"""
        if not cls.GROQ_API_KEY and not cls.OPENROUTER_API_KEY:
            logger.warning(
                "⚠️ No LLM API keys configured. Add at least one API key to .env file"
            )

        # Expand home directory
        cls.PROJECTS_DIR = os.path.expanduser(cls.PROJECTS_DIR)

        logger.info("✓ Configuration loaded successfully")
        if cls.ENABLE_VERBOSE_MODE:
            logger.info(f"Verbose mode enabled. Log level: {cls.LOG_LEVEL}")

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available LLM providers based on configured API keys"""
        providers = []
        if cls.GROQ_API_KEY:
            providers.append("groq")
        if cls.OPENROUTER_API_KEY:
            providers.append("openrouter")
        return providers


# Initialize configuration on module load
Config.validate()
