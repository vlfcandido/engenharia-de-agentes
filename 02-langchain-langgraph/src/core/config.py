"""Configuracao lida do .env (igual nos 3 projetos do repo).

Sem ANTHROPIC_API_KEY configurada, o projeto roda em MODO DEMO usando um modelo
de chat FAKE (offline), pra voce ver o grafo do LangGraph rodar de graca.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # anthropic | demo
    llm_provider: str = "demo"
    llm_model: str = "claude-sonnet-4-6"
    max_iters: int = 10

    anthropic_api_key: str = ""

    @property
    def provider_efetivo(self) -> str:
        if self.llm_provider == "anthropic" and self.anthropic_api_key:
            return "anthropic"
        return "demo"


settings = Settings()
