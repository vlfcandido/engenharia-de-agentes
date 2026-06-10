"""Exemplo executavel — mesmo exemplo dos outros projetos, agora com LangGraph.

Rode com:   python src/main.py
Sem ANTHROPIC_API_KEY no .env, roda em MODO DEMO (modelo fake offline).
"""

from __future__ import annotations

from agents.agente import Agente
from core.config import settings

# Mesma pergunta dos 3 projetos do repo, pra voce comparar as stacks.
PERGUNTA = "Quanto e (12 * 8) + 5? Salve o resultado nas minhas anotacoes."


def main() -> None:
    print("=" * 70)
    print("  AGENTE — LangChain + LangGraph")
    print(f"  Provedor: {settings.provider_efetivo}  |  max_iters: {settings.max_iters}")
    if settings.provider_efetivo == "demo":
        print("  (MODO DEMO — configure ANTHROPIC_API_KEY no .env pra usar o Claude)")
    print("=" * 70)
    print(f"\nPergunta: {PERGUNTA}")

    resposta = Agente().responder(PERGUNTA)

    print("\n" + "=" * 70)
    print("RESPOSTA FINAL:")
    print(resposta)
    print("=" * 70)


if __name__ == "__main__":
    main()
