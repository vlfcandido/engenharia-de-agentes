"""Configuracao do projeto, lida do arquivo .env de forma tipada.

Usa pydantic-settings: voce declara os campos uma vez e o Pydantic le do .env
(ou das variaveis de ambiente), valida os tipos e ja entrega tudo pronto.

Se nao houver chave de API configurada, `provider_efetivo` cai pra "demo" —
assim o projeto roda offline com um LLM mockado e voce ve a arquitetura
funcionando antes de configurar provedor de verdade.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


# C#: Settings e como uma classe de configuracao tipada (tipo IOptions<T>) que o
#     framework preenche a partir do .env. Cada campo abaixo e uma propriedade.
class Settings(BaseSettings):
    # Carrega o .env que estiver na raiz do projeto.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Qual provedor de LLM usar: anthropic | openai | gemini | demo
    llm_provider: str = "demo"

    # Modelo (vazio => default do provedor, definido em llm.py)
    llm_model: str = ""

    # Trava de seguranca: numero maximo de voltas do loop agentico.
    max_iters: int = 10

    # Chaves de API — preenchidas no .env. Vazias por padrao.
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    tavily_api_key: str = ""

    @property
    def provider_efetivo(self) -> str:
        """Provedor que sera realmente usado.

        Se o provedor escolhido nao tiver chave configurada, caimos pra "demo"
        em vez de quebrar. Isso deixa o `python src/main.py` rodar sempre.
        """
        chaves = {
            "anthropic": self.anthropic_api_key,
            "openai": self.openai_api_key,
            "gemini": self.google_api_key,
        }
        if self.llm_provider == "demo":
            return "demo"
        if not chaves.get(self.llm_provider):
            return "demo"
        return self.llm_provider


# Instancia unica, importada pelo resto do projeto.
settings = Settings()
