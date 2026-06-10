"""Exemplo executavel — mesmo exemplo dos outros projetos, agora com Google ADK.

Rode com:   python src/main.py
Sem GOOGLE_API_KEY no .env, roda em MODO DEMO (before_model_callback scriptado).
"""

from __future__ import annotations

import warnings

# ADK avisa que a geracao de schema por JSON e "experimental" — nao atrapalha.
warnings.filterwarnings("ignore", message=".*JSON_SCHEMA_FOR_FUNC_DECL.*")

from agents.agente import Agente  # noqa: E402
from core.config import settings  # noqa: E402

# Mesma pergunta dos 3 projetos do repo, pra voce comparar as stacks.
PERGUNTA = "Quanto e (12 * 8) + 5? Salve o resultado nas minhas anotacoes."


def main() -> None:
    print("=" * 70)
    print("  AGENTE — Google ADK")
    print(f"  Provedor: {settings.provider_efetivo}  |  modelo: {settings.llm_model}")
    if settings.provider_efetivo == "demo":
        print("  (MODO DEMO — configure GOOGLE_API_KEY no .env pra usar o Gemini)")
    print("=" * 70)
    print(f"\nPergunta: {PERGUNTA}")

    resposta = Agente().responder(PERGUNTA)

    print("\n" + "=" * 70)
    print("RESPOSTA FINAL:")
    print(resposta)
    print("=" * 70)


if __name__ == "__main__":
    main()
