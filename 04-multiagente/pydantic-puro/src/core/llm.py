"""Cliente de LLM dos agentes.

Cada agente chama `llm.gerar(prompt, papel=...)` e recebe TEXTO (JSON) de volta.
- AnthropicClient: Claude de verdade.
- DemoClient: cerebros mockados, um por papel (planejador/executor/revisor), pra
  o time multi-agente rodar OFFLINE e deterministico.

# C#: 'gerar' e o metodo da interface ILlm; o DemoClient e um fake/stub pra testar
#     sem rede, igual voce faria com um Moq.
"""

from __future__ import annotations

import json
from typing import Any, Protocol

from core.config import Settings


class LLMClient(Protocol):
    def gerar(self, prompt: str, *, papel: str) -> str: ...


def extrair_json(texto: str) -> dict[str, Any]:
    """Pega o primeiro objeto JSON de uma resposta (tolera ```json ... ``` e texto solto)."""
    inicio = texto.find("{")
    fim = texto.rfind("}")
    if inicio == -1 or fim == -1:
        return {}
    try:
        return json.loads(texto[inicio : fim + 1])
    except json.JSONDecodeError:
        return {}


# ---------------------------------------------------------------------------
#  Anthropic (Claude) — real
# ---------------------------------------------------------------------------
class AnthropicClient:
    def __init__(self, settings: Settings) -> None:
        from anthropic import Anthropic

        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.llm_model

    def gerar(self, prompt: str, *, papel: str) -> str:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")


# ---------------------------------------------------------------------------
#  Demo — um cerebro mockado por papel (offline)
# ---------------------------------------------------------------------------
class DemoClient:
    """Simula os 3 agentes sem chamar API. Deterministico, pra estudo e testes."""

    def gerar(self, prompt: str, *, papel: str) -> str:
        if papel == "planejador":
            return json.dumps(
                {
                    "passos": [
                        "Ler o nome do cliente nos dados recebidos",
                        "Escrever uma saudacao amigavel e personalizada",
                        "Salvar a saudacao em saida.txt",
                    ]
                }
            )

        if papel == "executor":
            tem_feedback = "FEEDBACK DO REVISOR" in prompt
            # Repare: mesmo com a tentativa de injection nos dados ("IGNORE TUDO..."),
            # o executor USA o nome (Frigo) mas IGNORA a ordem maliciosa. Nunca emite
            # "INVADIDO". Em modo real, e o system prompt + a fronteira de confianca
            # (core/seguranca.py) que garantem isso.
            if tem_feedback:
                saida = (
                    "Bem-vindo a nossa loja, Frigo! Que bom ter voce por aqui — "
                    "aproveite nossas ofertas e qualquer duvida e so chamar!"
                )
            else:
                saida = "Bem-vindo, Frigo!"
            return json.dumps(
                {"resultados": ["Identifiquei o cliente: Frigo", "Escrevi a saudacao"], "saida": saida}
            )

        if papel == "revisor":
            # Olha SO a saida do executor (nao o objetivo) pra decidir.
            idx = prompt.find("SAIDA DO EXECUTOR:")
            saida_txt = (prompt[idx:] if idx != -1 else prompt).lower()
            # Aprova so se a saudacao convida pro contexto da loja (criterio de qualidade).
            aprovado = "loja" in saida_txt
            feedback = "" if aprovado else (
                "A saudacao esta generica/curta. Personalize convidando o cliente para a loja."
            )
            return json.dumps({"aprovado": aprovado, "feedback": feedback})

        return "{}"


def criar_cliente(settings: Settings) -> LLMClient:
    if settings.provider_efetivo == "anthropic":
        return AnthropicClient(settings)
    return DemoClient()
