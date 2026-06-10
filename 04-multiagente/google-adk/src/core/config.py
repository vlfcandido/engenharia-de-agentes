"""Configuracao lida do .env (variante ADK). Sem chave => MODO DEMO."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "demo"  # gemini | demo
    llm_model: str = "gemini-2.0-flash"
    max_rounds: int = 3

    google_api_key: str = ""

    @property
    def provider_efetivo(self) -> str:
        if self.llm_provider == "gemini" and self.google_api_key:
            return "gemini"
        return "demo"


settings = Settings()
