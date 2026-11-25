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
    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        self.api_key = (
            api_key
            or os.getenv("OFFSPACE_OPENAI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        self.timeout = timeout

    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, prompt: str, **kwargs: Any) -> str:
        if not self.available():
            raise RuntimeError("OpenAI API key is not configured")
        try:
            import openai
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is missing") from exc

        try:
            client = openai.OpenAI(
                api_key=self.api_key,
                timeout=kwargs.get("timeout", self.timeout),
            )
            response = client.chat.completions.create(
                model=kwargs.get("model") or "gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 512),
                temperature=kwargs.get("temperature", 0.7),
            )
        except openai.APITimeoutError as exc:
            raise RuntimeError("OpenAI request timed out") from exc
        except openai.AuthenticationError as exc:
            raise RuntimeError("OpenAI authentication failed; check the configured API key") from exc
        except openai.APIConnectionError as exc:
            raise RuntimeError("OpenAI connection failed") from exc
        except openai.APIStatusError as exc:
            if exc.status_code == 404:
                raise RuntimeError(
                    "OpenAI model or endpoint was not found; check the configured model"
                ) from exc
            if exc.status_code == 429:
                raise RuntimeError("OpenAI request was rate-limited (status 429)") from exc
            raise RuntimeError(f"OpenAI request failed with status {exc.status_code}") from exc
        except openai.APIError as exc:
            raise RuntimeError("OpenAI request failed") from exc
        if not response.choices:
            raise RuntimeError("OpenAI returned no response choices")
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI returned an empty response")
        return content.strip()


class LocalModelProvider(BaseProvider):
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "llama3.2",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def available(self) -> bool:
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def chat(self, prompt: str, **kwargs: Any) -> str:
        if not self.available():
            raise RuntimeError(
                "Ollama is unavailable; start the local server with `ollama serve`"
            )
        try:
            import requests

            model = kwargs.get("model") or self.model
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
                timeout=kwargs.get("timeout", 60),
            )
            response.raise_for_status()
            content = response.json().get("message", {}).get("content")
            if not content:
                raise RuntimeError("Local AI returned an empty response")
            return content.strip()
        except requests.Timeout as exc:
            raise RuntimeError("Ollama request timed out") from exc
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else 0
            if status_code == 404:
                raise RuntimeError(
                    f"Ollama model '{model}' is unavailable; install it with "
                    f"`ollama pull {model}`"
                ) from exc
            raise RuntimeError(
                f"Ollama request failed with status {status_code}"
            ) from exc
        except requests.ConnectionError as exc:
            raise RuntimeError("Could not connect to the Ollama server") from exc
        except requests.RequestException as exc:
            raise RuntimeError("Ollama request failed due to a network error") from exc
