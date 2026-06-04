"""
LLM Provider Base Class
Abstract base for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class LLMResponse:
    """Standard response object from LLM providers"""

    def __init__(
        self,
        content: str,
        provider: str,
        model: str,
        tokens_used: int = 0,
        finish_reason: str = "stop",
        metadata: Dict[str, Any] = None,
    ):
        self.content = content
        self.provider = provider
        self.model = model
        self.tokens_used = tokens_used
        self.finish_reason = finish_reason
        self.metadata = metadata or {}

    def __repr__(self):
        return f"LLMResponse(provider={self.provider}, tokens={self.tokens_used}, reason={self.finish_reason})"


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: str, model: str = None):
        """
        Initialize provider

        Args:
            api_key: API key for the provider
            model: Model name to use
        """
        if not api_key:
            raise ValueError(f"API key required for {self.__class__.__name__}")

        self.api_key = api_key
        self.model = model or self.get_default_model()
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    @abstractmethod
    def get_default_model() -> str:
        """Get default model for this provider"""
        pass

    @staticmethod
    @abstractmethod
    def get_provider_name() -> str:
        """Get provider name"""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        Generate response from the LLM

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            LLMResponse object
        """
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from the LLM

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Yields:
            Text chunks as they arrive
        """
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (estimate if exact count not available)

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        pass

    async def validate_connection(self) -> bool:
        """
        Validate that connection to provider works

        Returns:
            True if connection is valid
        """
        try:
            response = await self.generate("Test connection", max_tokens=10)
            self.logger.info(f"✓ Connection to {self.get_provider_name()} validated")
            return True
        except Exception as e:
            self.logger.error(f"✗ Connection validation failed: {str(e)}")
            return False
