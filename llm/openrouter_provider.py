"""
OpenRouter LLM Provider
Implementation for OpenRouter API with SSL and error handling
"""

import aiohttp
import asyncio
import logging
import json
import ssl
import certifi
from typing import Optional, AsyncGenerator

from llm.provider_base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API Provider"""

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model)
        self.base_url = "https://openrouter.io/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/lariabali/agent-system",
            "X-Title": "Agent System",
        }
        # SSL context with certificate verification
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    @staticmethod
    def get_provider_name() -> str:
        return "OpenRouter"

    @staticmethod
    def get_default_model() -> str:
        return "meta-llama/llama-3-70b-instruct"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate response from OpenRouter API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=self.ssl_context)
            ) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"OpenRouter error {response.status}: {error_text}")

                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    tokens_used = data.get("usage", {}).get("total_tokens", 0)

                    return LLMResponse(
                        content=content,
                        provider="openrouter",
                        model=self.model,
                        tokens_used=tokens_used,
                        finish_reason=data["choices"][0].get("finish_reason", "stop"),
                    )

        except asyncio.TimeoutError:
            logger.error("OpenRouter request timed out")
            raise
        except Exception as e:
            logger.error(f"OpenRouter generation error: {str(e)}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """Stream response from OpenRouter API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }

            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=self.ssl_context)
            ) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"OpenRouter error {response.status}: {error_text}")

                    async for line in response.content:
                        if line:
                            line = line.decode("utf-8").strip()
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if (
                                        "choices" in data
                                        and data["choices"]
                                        and "delta" in data["choices"][0]
                                    ):
                                        content = data["choices"][0]["delta"].get("content", "")
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue

        except asyncio.TimeoutError:
            logger.error("OpenRouter stream request timed out")
            raise
        except Exception as e:
            logger.error(f"OpenRouter stream generation error: {str(e)}")
            raise

    async def count_tokens(self, text: str) -> int:
        """
        Estimate token count for OpenRouter
        Rough estimation: 1 token ≈ 4 characters
        """
        estimated_tokens = len(text) // 4
        return max(1, estimated_tokens)

    async def validate_connection(self) -> bool:
        """Validate OpenRouter connection with SSL handling"""
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10,
            }

            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=self.ssl_context)
            ) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        logger.info("✓ OpenRouter connection validated successfully")
                        return True
                    else:
                        logger.error(f"✗ OpenRouter connection failed: {response.status}")
                        return False
        except asyncio.TimeoutError:
            logger.error("✗ OpenRouter connection validation timed out")
            return False
        except Exception as e:
            logger.error(f"✗ OpenRouter connection validation failed: {str(e)}")
            return False
