from typing import Dict, Optional

from .provider import BaseProvider, LocalModelProvider, OpenAIProvider


class ModelRouter:
    def __init__(self, config: Optional[Dict[str, str]] = None):
        self.config = config or {}
        self.providers: Dict[str, BaseProvider] = {
            "openai": OpenAIProvider(api_key=self.config.get("OPENAI_API_KEY")),
            "local": LocalModelProvider(
                base_url=self.config.get("LOCAL_AI_URL", "http://127.0.0.1:11434"),
                model=self.config.get("LOCAL_AI_MODEL", "llama3.2"),
            ),
        }
        self.default_provider = self.config.get("DEFAULT_PROVIDER", "openai")

    def get_provider(self, name: Optional[str] = None) -> BaseProvider:
        provider_name = (name or self.default_provider).lower()
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self.providers[provider_name]

    def chat(self, prompt: str, provider_name: Optional[str] = None, **kwargs: object) -> str:
        selected_provider = (provider_name or self.default_provider).lower()
        provider = self.get_provider(selected_provider)
        if not provider.available():
            if selected_provider == "openai":
                raise RuntimeError(
                    "OpenAI is unavailable; configure OPENAI_API_KEY or "
                    "OFFSPACE_OPENAI_API_KEY"
                )
            raise RuntimeError(
                "Ollama is unavailable; start it with `ollama serve` and verify "
                "the configured model is installed"
            )
        return provider.chat(prompt, **kwargs)
