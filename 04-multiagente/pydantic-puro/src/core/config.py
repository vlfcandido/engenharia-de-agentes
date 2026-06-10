"""Configuracao lida do .env. Sem chave => MODO DEMO (cerebros mockados)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "demo"  # anthropic | demo
    llm_model: str = "claude-sonnet-4-6"
    max_rounds: int = 3  # quantas vezes o revisor pode mandar de volta pro executor

    anthropic_api_key: str = ""

    @property
    def provider_efetivo(self) -> str:
        if self.llm_provider == "anthropic" and self.anthropic_api_key:
            return "anthropic"
        return "demo"


settings = Settings()
