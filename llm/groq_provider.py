"""
Groq Cloud Console LLM Provider
Implementation for Groq Cloud API
"""

import asyncio
import logging
from typing import Optional, AsyncGenerator

try:
    from groq import Groq, AsyncGroq
except ImportError:
    raise ImportError("groq package not installed. Install it with: pip install groq")

from llm.provider_base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq Cloud Console API Provider"""

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model)
        self.client = AsyncGroq(api_key=api_key)
        self.sync_client = Groq(api_key=api_key)

    @staticmethod
    def get_provider_name() -> str:
        return "Groq"

    @staticmethod
    def get_default_model() -> str:
        return "llama-3.3-70b-versatile"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate response from Groq API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            return LLMResponse(
                content=content,
                provider="groq",
                model=self.model,
                tokens_used=tokens_used,
                finish_reason=response.choices[0].finish_reason,
            )

        except Exception as e:
            error_msg = str(e).lower()
            if "decommissioned" in error_msg or "not found" in error_msg:
                logger.error(
                    f"Groq model '{self.model}' is deprecated or not available. "
                    f"Error: {str(e)}"
                )
            else:
                logger.error(f"Groq generation error: {str(e)}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """Stream response from Groq API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Groq stream generation error: {str(e)}")
            raise

    async def count_tokens(self, text: str) -> int:
        """
        Estimate token count for Groq
        Groq doesn't have a token counting API, so we estimate
        """
        # Rough estimation: 1 token ≈ 4 characters
        estimated_tokens = len(text) // 4
        return max(1, estimated_tokens)

    async def validate_connection(self) -> bool:
        """Validate Groq connection"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            logger.info("✓ Groq connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Groq connection validation failed: {str(e)}")
            return False
