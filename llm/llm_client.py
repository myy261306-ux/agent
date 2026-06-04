"""
LLM Client Orchestrator
Main interface that manages all LLM providers with fallback strategy
"""

import logging
import asyncio
from typing import Optional, AsyncGenerator, List
from dataclasses import dataclass

from utils.config import Config
from llm.provider_base import LLMResponse, BaseLLMProvider
from llm.groq_provider import GroqProvider
from llm.openrouter_provider import OpenRouterProvider

logger = logging.getLogger(__name__)


@dataclass
class ProviderStatus:
    """Status of an LLM provider"""

    name: str
    available: bool
    response_time: float = 0.0
    error_message: str = ""


class LLMClient:
    """
    Main LLM client that manages all providers
    Implements fallback strategy: Groq → OpenRouter
    """

    def __init__(self):
        self.providers: List[BaseLLMProvider] = []
        self.provider_order: List[str] = []
        self.status: dict[str, ProviderStatus] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize available providers based on configuration"""
        logger.info("🚀 Initializing LLM Providers...")

        # Priority order: Groq → OpenRouter
        if Config.GROQ_API_KEY:
            try:
                self.providers.append(GroqProvider(Config.GROQ_API_KEY, Config.GROQ_MODEL))
                self.provider_order.append("groq")
                self.status["groq"] = ProviderStatus(name="Groq", available=False)
                logger.info("  ✓ Groq provider loaded")
            except Exception as e:
                logger.warning(f"  ✗ Groq provider failed to load: {str(e)}")

        if Config.OPENROUTER_API_KEY:
            try:
                self.providers.append(OpenRouterProvider(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL))
                self.provider_order.append("openrouter")
                self.status["openrouter"] = ProviderStatus(name="OpenRouter", available=False)
                logger.info("  ✓ OpenRouter provider loaded")
            except Exception as e:
                logger.warning(f"  ✗ OpenRouter provider failed to load: {str(e)}")

        # Warning message if no providers are available
        if not self.providers:
            warning_msg = (
                "⚠️ No LLM providers configured!\n"
                "Please add API keys to .env file:\n"
                "  - GROQ_API_KEY (Primary)\n"
                "  - OPENROUTER_API_KEY (Fallback)\n\n"
                "Get keys from:\n"
                "  • Groq: https://console.groq.com\n"
                "  • OpenRouter: https://openrouter.ai/keys"
            )
            logger.warning(warning_msg)
            raise RuntimeError(warning_msg)

        logger.info(f"✓ {len(self.providers)} LLM provider(s) initialized (Priority: {' → '.join(self.provider_order).upper()})")

    async def validate_all_connections(self) -> dict[str, bool]:
        """
        Validate connections to all providers

        Returns:
            Dictionary mapping provider names to connection status
        """
        logger.info("🔍 Validating provider connections...")
        results = {}

        for provider in self.providers:
            try:
                is_valid = await provider.validate_connection()
                results[provider.get_provider_name().lower()] = is_valid
                if is_valid:
                    logger.info(f"  ✓ {provider.get_provider_name()} is available")
                else:
                    logger.warning(f"  ⚠ {provider.get_provider_name()} connection failed")
            except Exception as e:
                logger.error(f"  ✗ {provider.get_provider_name()} validation error: {str(e)}")
                results[provider.get_provider_name().lower()] = False

        return results

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = None,
    ) -> LLMResponse:
        """
        Generate response with automatic fallback

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds

        Returns:
            LLMResponse from available provider

        Raises:
            RuntimeError: If all providers fail
        """
        timeout = timeout or Config.REQUEST_TIMEOUT

        errors = []

        for i, provider in enumerate(self.providers):
            try:
                logger.debug(
                    f"Attempting generation with {provider.get_provider_name()} ({i+1}/{len(self.providers)})"
                )

                response = await asyncio.wait_for(
                    provider.generate(prompt, system_prompt, temperature, max_tokens),
                    timeout=timeout,
                )

                logger.info(
                    f"✓ Response generated by {provider.get_provider_name()} ({response.tokens_used} tokens)"
                )
                return response

            except asyncio.TimeoutError:
                error = f"{provider.get_provider_name()} timed out"
                logger.warning(f"⏱ {error}")
                errors.append(error)
            except Exception as e:
                error = f"{provider.get_provider_name()} failed: {str(e)}"
                logger.warning(f"⚠ {error}")
                errors.append(error)

        # All providers failed
        error_msg = "All LLM providers exhausted. Errors: " + "; ".join(errors)
        logger.error(f"❌ {error_msg}")
        raise RuntimeError(error_msg)

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream response with automatic fallback

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds

        Yields:
            Text chunks as they arrive

        Raises:
            RuntimeError: If all providers fail
        """
        timeout = timeout or Config.REQUEST_TIMEOUT
        errors = []

        for i, provider in enumerate(self.providers):
            try:
                logger.debug(
                    f"Attempting stream generation with {provider.get_provider_name()} ({i+1}/{len(self.providers)})"
                )

                async for chunk in asyncio.wait_for(
                    provider.stream_generate(prompt, system_prompt, temperature, max_tokens),
                    timeout=timeout,
                ):
                    yield chunk

                logger.info(f"✓ Stream completed from {provider.get_provider_name()}")
                return

            except asyncio.TimeoutError:
                error = f"{provider.get_provider_name()} stream timed out"
                logger.warning(f"⏱ {error}")
                errors.append(error)
            except Exception as e:
                error = f"{provider.get_provider_name()} stream failed: {str(e)}"
                logger.warning(f"⚠ {error}")
                errors.append(error)

        # All providers failed
        error_msg = "All LLM providers failed for streaming. Errors: " + "; ".join(errors)
        logger.error(f"❌ {error_msg}")
        raise RuntimeError(error_msg)

    def get_provider_info(self) -> dict:
        """Get information about all available providers"""
        return {
            "total_providers": len(self.providers),
            "provider_order": self.provider_order,
            "providers": [
                {
                    "name": p.get_provider_name(),
                    "model": p.model,
                    "status": self.status.get(p.get_provider_name().lower(), {})
                }
                for p in self.providers
            ],
        }
