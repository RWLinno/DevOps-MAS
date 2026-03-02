"""
API-based LLM Provider
Supports OpenAI-compatible APIs (OpenAI, Azure, local Ollama, vLLM, etc.)
Enables standalone operation without internal platform dependencies.
"""

import asyncio
import base64
import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    success: bool = True
    error: Optional[str] = None
    model: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0
    tool_calls: Optional[List[Dict[str, Any]]] = None


class APIModelProvider:
    """
    Unified API-based LLM provider supporting:
    - OpenAI / GPT-4o / GPT-4-vision
    - Azure OpenAI
    - Ollama (local deployment)
    - Any OpenAI-compatible endpoint (vLLM, LMStudio, etc.)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.provider = self.config.get("provider", os.getenv("LLM_PROVIDER", "openai"))

        self.api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY", "")
        self.base_url = self.config.get("base_url") or os.getenv(
            "OPENAI_BASE_URL", self._default_base_url()
        )
        self.default_model = self.config.get("model") or os.getenv(
            "LLM_MODEL", "gpt-4o-mini"
        )
        self.timeout = self.config.get("timeout", 60)
        self.max_retries = self.config.get("max_retries", 3)

        self._session: Optional[aiohttp.ClientSession] = None
        logger.info(
            f"APIModelProvider initialized: provider={self.provider}, "
            f"model={self.default_model}, base_url={self.base_url}"
        )

    def _default_base_url(self) -> str:
        urls = {
            "openai": "https://api.openai.com/v1",
            "azure": self.config.get("azure_endpoint", ""),
            "ollama": "http://localhost:11434/v1",
            "local": "http://localhost:8000/v1",
        }
        return urls.get(self.provider, "https://api.openai.com/v1")

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )
        return self._session

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: Optional[List[Dict[str, Any]]] = None,
        image: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            messages: Chat messages in OpenAI format.
            model: Override model name.
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.
            tools: Tool definitions for function calling.
            image: Image path, URL, or base64 string for vision models.
        """
        use_model = model or self.default_model
        start_time = time.time()

        if image:
            messages = self._inject_image(messages, image)

        payload: Dict[str, Any] = {
            "model": use_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        payload.update(kwargs)

        for attempt in range(self.max_retries):
            try:
                session = await self._get_session()
                url = f"{self.base_url.rstrip('/')}/chat/completions"

                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(
                            f"API returned {resp.status}: {error_text[:500]}"
                        )

                    data = await resp.json()
                    choice = data["choices"][0]
                    message = choice.get("message", {})

                    tool_calls = None
                    if message.get("tool_calls"):
                        tool_calls = [
                            {
                                "id": tc.get("id"),
                                "function": {
                                    "name": tc["function"]["name"],
                                    "arguments": tc["function"]["arguments"],
                                },
                            }
                            for tc in message["tool_calls"]
                        ]

                    return LLMResponse(
                        content=message.get("content", "") or "",
                        success=True,
                        model=data.get("model", use_model),
                        usage=data.get("usage", {}),
                        latency_ms=(time.time() - start_time) * 1000,
                        tool_calls=tool_calls,
                    )

            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries}")
            except Exception as e:
                logger.warning(
                    f"API error on attempt {attempt + 1}/{self.max_retries}: {e}"
                )
                if attempt == self.max_retries - 1:
                    return LLMResponse(
                        content="",
                        success=False,
                        error=str(e),
                        latency_ms=(time.time() - start_time) * 1000,
                    )
            await asyncio.sleep(0.5 * (2 ** attempt))

        return LLMResponse(
            content="",
            success=False,
            error="All retry attempts failed",
            latency_ms=(time.time() - start_time) * 1000,
        )

    def _inject_image(
        self, messages: List[Dict[str, Any]], image_source: str
    ) -> List[Dict[str, Any]]:
        """Inject image into the last user message for vision models."""
        image_url = self._resolve_image_url(image_source)
        if not image_url:
            return messages

        messages = [dict(m) for m in messages]
        for i in range(len(messages) - 1, -1, -1):
            if messages[i]["role"] == "user":
                content = messages[i].get("content", "")
                if isinstance(content, str):
                    messages[i]["content"] = [
                        {"type": "text", "text": content},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]
                elif isinstance(content, list):
                    content.append(
                        {"type": "image_url", "image_url": {"url": image_url}}
                    )
                break
        return messages

    @staticmethod
    def _resolve_image_url(image_source: str) -> Optional[str]:
        if image_source.startswith(("http://", "https://")):
            return image_source
        if image_source.startswith("data:image"):
            return image_source
        if os.path.isfile(image_source):
            ext = Path(image_source).suffix.lstrip(".").lower()
            mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp", "gif": "gif"}
            mime_type = mime.get(ext, "jpeg")
            with open(image_source, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f"data:image/{mime_type};base64,{b64}"
        try:
            base64.b64decode(image_source)
            return f"data:image/jpeg;base64,{image_source}"
        except Exception:
            return None

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
