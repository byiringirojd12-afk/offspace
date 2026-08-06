import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseProvider(ABC):
    @abstractmethod
    def chat(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, prompt: str, **kwargs: Any) -> str:
        if not self.available():
            raise RuntimeError("OpenAI API key is not configured")
        try:
            import openai
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is missing") from exc

        response = openai.ChatCompletion.create(
            model=kwargs.get("model", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 512),
            temperature=kwargs.get("temperature", 0.7),
        )
        return response.choices[0].message.content.strip()


class LocalModelProvider(BaseProvider):
    def available(self) -> bool:
        return False

    def chat(self, prompt: str, **kwargs: Any) -> str:
        raise RuntimeError("Local models are not available in this environment")
