import os
import secrets

from pydantic import AliasChoices, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="OFFSPACE_",
    )

    app_name: str = Field("Offspace Backend")
    api_version: str = Field("1.0.0")
    environment: str = Field("development")
    debug: bool = Field(False)
    database_url: str = Field("sqlite:///./offspace.db")
    secret_key: SecretStr = Field(default_factory=lambda: SecretStr(os.getenv("OFFSPACE_SECRET_KEY") or os.getenv("JWT_SECRET_KEY") or secrets.token_hex(32)))
    jwt_algorithm: str = Field("HS256")
    token_expiration_seconds: int = Field(3600)
    refresh_token_expiration_seconds: int = Field(86400)
    allowed_origins: list[str] = Field([
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "tauri://localhost",
        "http://tauri.localhost",
    ])
    openai_api_key: str | None = Field(
        None,
        validation_alias=AliasChoices("OFFSPACE_OPENAI_API_KEY", "OPENAI_API_KEY"),
    )
    default_provider: str = Field("openai")
    local_ai_url: str = Field("http://127.0.0.1:11434")
    local_ai_model: str = Field("llama3.2")

    @field_validator("secret_key", mode="before")
    @classmethod
    def _validate_secret_key(cls, value):
        if isinstance(value, str):
            return SecretStr(value)
        return value

    @model_validator(mode="after")
    def check_production_secret(self):
        if self.environment == "production" and self.secret_key.get_secret_value() == "":
            raise ValueError("OFFSPACE_SECRET_KEY or JWT_SECRET_KEY must be set in production")
        return self


settings = Settings()
