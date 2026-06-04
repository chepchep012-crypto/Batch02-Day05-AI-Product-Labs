from __future__ import annotations

import json
import os
from typing import Any

from services.providers.base import ModelResponse, ToolCall


class OpenAIProvider:
    """Async OpenAI Chat Completions — also works for any OpenAI-compatible endpoint."""

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.default_model = default_model

    async def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise RuntimeError("pip install openai") from exc

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing env var: {self.api_key_env}")

        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": int(os.getenv("MAX_TOKENS", "1500")),
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        client = AsyncOpenAI(
            api_key=api_key,
            **({} if not self.base_url else {"base_url": self.base_url}),
        )
        resp = await client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        calls: list[ToolCall] = []
        for tc in msg.tool_calls or []:
            args = json.loads(tc.function.arguments or "{}")
            calls.append(ToolCall(name=tc.function.name, args=args))

        usage: dict[str, int] | None = None
        if resp.usage:
            usage = {
                "prompt_tokens":     resp.usage.prompt_tokens or 0,
                "completion_tokens": resp.usage.completion_tokens or 0,
                "total_tokens":      resp.usage.total_tokens or 0,
            }
        return ModelResponse(text=msg.content, tool_calls=calls, raw=resp, usage=usage)
