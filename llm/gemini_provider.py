"""
Google Gemini 2.5 Pro LLM Provider
Implementation for Google Generative AI API
"""

import logging
from typing import Optional, AsyncGenerator

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError(
        "google-generativeai package not installed. Install it with: pip install google-generativeai"
    )

from llm.provider_base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini 2.5 Pro API Provider"""

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)

    @staticmethod
    def get_provider_name() -> str:
        return "Gemini"

    @staticmethod
    def get_default_model() -> str:
        return "gemini-2.5-pro"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate response from Gemini API"""
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            generation_config = genai.types.GenerationConfig(
                temperature=temperature, max_output_tokens=max_tokens
            )

            # Gemini doesn't support async directly in this wrapper
            # We'll run it in thread pool
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate_content(
                    full_prompt, generation_config=generation_config
                ),
            )

            content = response.text
            # Gemini doesn't provide token count, estimate based on text
            tokens_used = await self.count_tokens(content)

            return LLMResponse(
                content=content,
                provider="gemini",
                model=self.model,
                tokens_used=tokens_used,
                finish_reason="stop",
            )

        except Exception as e:
            logger.error(f"Gemini generation error: {str(e)}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """Stream response from Gemini API"""
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            generation_config = genai.types.GenerationConfig(
                temperature=temperature, max_output_tokens=max_tokens
            )

            import asyncio

            loop = asyncio.get_event_loop()
            stream = await loop.run_in_executor(
                None,
                lambda: self.client.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                    stream=True,
                ),
            )

            for chunk in stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini stream generation error: {str(e)}")
            raise

    async def count_tokens(self, text: str) -> int:
        """
        Count tokens using Gemini's token counter
        Falls back to estimation if counter not available
        """
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: genai.count_tokens(text),
            )
            return response.total_tokens
        except Exception:
            # Fallback: estimate 1 token ≈ 4 characters
            estimated_tokens = len(text) // 4
            return max(1, estimated_tokens)

    async def validate_connection(self) -> bool:
        """Validate Gemini connection"""
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.generate_content("Hello", stream=False),
            )
            logger.info("✓ Gemini connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Gemini connection validation failed: {str(e)}")
            return False
