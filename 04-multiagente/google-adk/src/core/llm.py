"""Cliente de LLM (variante ADK).

Cada papel (planejador/executor/revisor) e executado como um **LlmAgent real do
ADK**, rodado via Runner. Em MODO DEMO, um `before_model_callback` scriptado
devolve a resposta offline (mesma tecnica do projeto 03) — assim o time multi-agente
roda sem chave, exercitando de verdade o Runner e os callbacks do ADK.

Os agentes de logica (PlannerAgent/ExecutorAgent/ReviewerAgent) e o orquestrador
sao os MESMOS dos outros variantes — so este cliente muda.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Protocol

from core.config import Settings


class LLMClient(Protocol):
    def gerar(self, prompt: str, *, papel: str) -> str: ...


def extrair_json(texto: str) -> dict[str, Any]:
    inicio, fim = texto.find("{"), texto.rfind("}")
    if inicio == -1 or fim == -1:
        return {}
    try:
        return json.loads(texto[inicio : fim + 1])
    except json.JSONDecodeError:
        return {}


def resposta_demo(papel: str, prompt: str) -> str:
    """Cerebro mockado por papel (offline) — identico aos outros variantes."""
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
        # Usa o nome (Frigo) mas IGNORA a ordem maliciosa dos dados. Nunca "INVADIDO".
        if tem_feedback:
            saida = (
                "Bem-vindo a nossa loja, Frigo! Que bom ter voce por aqui — "
                "aproveite nossas ofertas e qualquer duvida e so chamar!"
            )
        else:
            saida = "Bem-vindo, Frigo!"
        return json.dumps({"resultados": ["Identifiquei o cliente: Frigo", "Escrevi a saudacao"], "saida": saida})
    if papel == "revisor":
        idx = prompt.find("SAIDA DO EXECUTOR:")
        saida_txt = (prompt[idx:] if idx != -1 else prompt).lower()
        aprovado = "loja" in saida_txt
        feedback = "" if aprovado else "A saudacao esta generica/curta. Personalize convidando o cliente para a loja."
        return json.dumps({"aprovado": aprovado, "feedback": feedback})
    return "{}"


class AdkClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.demo = settings.provider_efetivo == "demo"

    def gerar(self, prompt: str, *, papel: str) -> str:
        return asyncio.run(self._rodar(prompt, papel))

    async def _rodar(self, prompt: str, papel: str) -> str:
        from google.adk.agents import LlmAgent
        from google.adk.models import LlmResponse
        from google.adk.runners import InMemoryRunner
        from google.genai import types

        before = None
        if self.demo:
            def before(callback_context: Any, llm_request: Any) -> LlmResponse:
                texto = resposta_demo(papel, prompt)
                return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=texto)]))

        agent = LlmAgent(
            name=papel,
            model=self.settings.llm_model,
            instruction="Responda exatamente no formato JSON pedido no prompt.",
            before_model_callback=before,
        )
        runner = InMemoryRunner(agent=agent, app_name="multi")
        await runner.session_service.create_session(app_name="multi", user_id="u", session_id="s")
        msg = types.Content(role="user", parts=[types.Part(text=prompt)])
        texto = ""
        async for event in runner.run_async(user_id="u", session_id="s", new_message=msg):
            if event.content and event.content.parts:
                for p in event.content.parts:
                    if p.text:
                        texto = p.text
        return texto


def criar_cliente(settings: Settings) -> LLMClient:
    return AdkClient(settings)
