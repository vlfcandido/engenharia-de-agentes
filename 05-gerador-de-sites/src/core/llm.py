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
                {"passos": ["Hero (chamada principal)", "Sobre", "Cardapio/Servicos", "Contato"]}
            )

        if papel == "executor":
            from site_templates import css, pagina_html

            # Dados do negocio (viriam de um formulario). Hardcoded no demo; em modo
            # real o LLM le isso dos DADOS, sempre tratando-os como dados (seguranca).
            nome, email = "Cafe do Frigo", "contato@cafedofrigo.com"
            tem_feedback = "FEEDBACK DO REVISOR" in prompt
            # Round 1: site incompleto (so hero+sobre). Round 2 (com feedback): completo.
            completo = tem_feedback
            arquivos = {
                "site/index.html": pagina_html(nome, email, completo),
                "site/style.css": css(),
            }
            if completo:
                saida = "Gerei o site completo com as secoes: hero, sobre, cardapio (servicos) e contato."
            else:
                saida = "Gerei o site com as secoes: hero e sobre."
            return json.dumps({"arquivos": arquivos, "saida": saida})

        if papel == "revisor":
            idx = prompt.find("SAIDA DO EXECUTOR:")
            saida_txt = (prompt[idx:] if idx != -1 else prompt).lower()
            # Criterio de qualidade: o site precisa ter secao de CONTATO.
            aprovado = "contato" in saida_txt
            feedback = "" if aprovado else (
                "Faltam secoes essenciais: inclua um Cardapio/Servicos e uma secao de Contato."
            )
            return json.dumps({"aprovado": aprovado, "feedback": feedback})

        return "{}"


def criar_cliente(settings: Settings) -> LLMClient:
    if settings.provider_efetivo == "anthropic":
        return AnthropicClient(settings)
    return DemoClient()
