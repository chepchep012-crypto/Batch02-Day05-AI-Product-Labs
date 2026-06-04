from __future__ import annotations

import os
from typing import Any

from services.providers.base import ModelResponse, ToolCall


class AnthropicProvider:
    """Async Anthropic Claude with native tool_use support."""

    def __init__(self) -> None:
        self.default_model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")

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
            import anthropic
        except ImportError as exc:
            raise RuntimeError("pip install anthropic") from exc

        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise RuntimeError("Missing env var: CLAUDE_API_KEY")

        # Convert OpenAI-style tools → Anthropic input_schema format
        claude_tools = []
        for t in (tools or []):
            fn = t["function"]
            claude_tools.append({
                "name": fn["name"],
                "description": fn.get("description", ""),
                "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
            })

        # Separate system message from conversation messages
        system_content = ""
        conv_messages = []
        for m in messages:
            if m["role"] == "system":
                system_content = m["content"] if isinstance(m["content"], str) else ""
            else:
                conv_messages.append(m)

        client = anthropic.AsyncAnthropic(api_key=api_key)
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "max_tokens": 2500,
            "temperature": temperature,
            "messages": conv_messages,
        }
        if system_content:
            kwargs["system"] = system_content
        if claude_tools:
            kwargs["tools"] = claude_tools

        resp = await client.messages.create(**kwargs)

        tool_uses   = [b for b in resp.content if b.type == "tool_use"]
        text_blocks = [b for b in resp.content if b.type == "text"]

        calls = [ToolCall(name=tu.name, args=tu.input) for tu in tool_uses]
        text  = text_blocks[0].text if text_blocks else None

        usage = {
            "prompt_tokens":     resp.usage.input_tokens,
            "completion_tokens": resp.usage.output_tokens,
            "total_tokens":      resp.usage.input_tokens + resp.usage.output_tokens,
        }
        return ModelResponse(text=text, tool_calls=calls, raw=resp, usage=usage)
