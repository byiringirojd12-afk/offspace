from typing import Dict, Optional

from .provider import BaseProvider, LocalModelProvider, OpenAIProvider


class ModelRouter:
    def __init__(self, config: Optional[Dict[str, str]] = None):
        self.config = config or {}
        self.providers: Dict[str, BaseProvider] = {
            "openai": OpenAIProvider(api_key=self.config.get("OPENAI_API_KEY")),
            "local": LocalModelProvider(),
        }
        self.default_provider = self.config.get("DEFAULT_PROVIDER", "openai")

    def get_provider(self, name: Optional[str] = None) -> BaseProvider:
        provider_name = (name or self.default_provider).lower()
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self.providers[provider_name]

    def chat(self, prompt: str, provider_name: Optional[str] = None, **kwargs: object) -> str:
        provider = self.get_provider(provider_name)
        if not provider.available():
            raise RuntimeError(f"Provider {provider_name or self.default_provider} is unavailable")
        return provider.chat(prompt, **kwargs)
