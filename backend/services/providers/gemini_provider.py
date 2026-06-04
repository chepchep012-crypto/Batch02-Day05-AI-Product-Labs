from __future__ import annotations

import os

from services.providers.openai_provider import OpenAIProvider


class GeminiProvider(OpenAIProvider):
    """
    Gemini via Google's OpenAI-compatible endpoint.
    Supports function calling with the same OpenAI SDK.
    """

    def __init__(self) -> None:
        super().__init__(
            api_key_env="GEMINI_API_KEY",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            default_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        )
