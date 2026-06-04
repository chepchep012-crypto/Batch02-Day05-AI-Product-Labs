from __future__ import annotations

import os

from services.providers.openai_provider import OpenAIProvider
from services.providers.openrouter_provider import OpenRouterProvider
from services.providers.gemini_provider import GeminiProvider
from services.providers.anthropic_provider import AnthropicProvider


def make_provider(name: str):
    """Factory — return the right provider instance by name."""
    name = name.lower().strip()
    if name == "openai":
        return OpenAIProvider(
            api_key_env="OPENAI_API_KEY",
            default_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )
    if name == "openrouter":
        return OpenRouterProvider()
    if name == "gemini":
        return GeminiProvider()
    if name in ("claude", "anthropic"):
        return AnthropicProvider()
    if name == "ollama":
        return OpenAIProvider(
            api_key_env="OLLAMA_API_KEY",  # can be any value
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/v1",
            default_model=os.getenv("OLLAMA_MODEL", "llama3"),
        )
    raise ValueError(f"Unknown provider: {name!r}. Choose openai|openrouter|gemini|claude|ollama")


def detect_provider_name() -> str:
    """Auto-detect provider from env vars, same order as chatbot.py."""
    explicit = os.getenv("AI_PROVIDER", "").lower().strip()
    if explicit in ("openai", "gemini", "claude", "openrouter", "ollama"):
        return explicit
    if os.getenv("OPENAI_API_KEY", "").strip():
        return "openai"
    if os.getenv("GEMINI_API_KEY", "").strip():
        return "gemini"
    if os.getenv("CLAUDE_API_KEY", "").strip():
        return "claude"
    if os.getenv("OPENROUTER_API_KEY", "").strip():
        return "openrouter"
    return "ollama"
