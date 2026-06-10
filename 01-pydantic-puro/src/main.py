"""Exemplo executavel — Agente do Zero em Python puro + Pydantic.

Rode com:   python src/main.py
         (ou, mais facil:  ..\scripts\run.ps1  no Windows)

Sem chave de API no .env, roda em MODO DEMO (LLM mockado) e voce ve o loop
agentico funcionando de graca. Com ANTHROPIC_API_KEY no .env, usa o Claude.

Este MESMO exemplo (mesma pergunta, mesmas tools) existe nos 3 projetos do repo
(Pydantic puro / LangChain+LangGraph / Google ADK) pra voce comparar as stacks.
"""

from __future__ import annotations

from agents.agente import Agente
from core.config import settings
from core.hooks import Hooks, hook_de_log
from tools.anotacoes import anotacoes
from tools.calculadora import calculadora

# A pergunta que o agente vai resolver. Ele precisa CALCULAR e depois SALVAR —
# ou seja, usar duas tools em sequencia, mostrando o loop de varias iteracoes.
PERGUNTA = "Quanto e (12 * 8) + 5? Salve o resultado nas minhas anotacoes."


def main() -> None:
    print("=" * 70)
    print("  AGENTE DO ZERO — Pydantic puro")
    print(f"  Provedor: {settings.provider_efetivo}  |  max_iters: {settings.max_iters}")
    if settings.provider_efetivo == "demo":
        print("  (MODO DEMO — configure uma chave no .env pra usar um LLM real)")
    print("=" * 70)
    print(f"\nPergunta: {PERGUNTA}")

    # Monta o agente: registra hooks de log e as duas tools de exemplo.
    hooks = hook_de_log(Hooks())
    agente = Agente(hooks=hooks)
    agente.adicionar_tool(calculadora).adicionar_tool(anotacoes)

    resposta = agente.responder(PERGUNTA)

    print("\n" + "=" * 70)
    print("RESPOSTA FINAL:")
    print(resposta)
    print("=" * 70)


if __name__ == "__main__":
    main()
