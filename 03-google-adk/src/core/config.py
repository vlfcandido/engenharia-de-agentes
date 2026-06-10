"""Configuracao lida do .env (igual nos 3 projetos do repo).

Sem GOOGLE_API_KEY configurada, roda em MODO DEMO: um before_model_callback
scriptado simula as respostas do Gemini offline (sem custo). As TOOLS rodam
de verdade — so a "decisao" do modelo e que e simulada.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # gemini | demo
    llm_provider: str = "demo"
    llm_model: str = "gemini-2.0-flash"
    max_iters: int = 10

    google_api_key: str = ""

    @property
    def provider_efetivo(self) -> str:
        if self.llm_provider == "gemini" and self.google_api_key:
            return "gemini"
        return "demo"


settings = Settings()
