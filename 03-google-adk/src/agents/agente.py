"""Agente ADK — monta o LlmAgent + Runner e expoe um `responder()` simples.

Mesma ideia dos outros projetos: junta cerebro (modelo) + maos (tools) +
sensores (callbacks). Aqui o "loop" e o proprio Runner do ADK.
"""

from __future__ import annotations

import asyncio

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

from core import callbacks
from core.config import Settings, settings as settings_global
from tools.ferramentas import TOOLS

_APP = "agentic-adk"
_USER = "frigo"


class Agente:
    def __init__(self, *, settings: Settings | None = None) -> None:
        self.settings = settings or settings_global
        demo = self.settings.provider_efetivo == "demo"

        # before_model: em demo, o driver scriptado (offline); em real, so loga.
        before_model = callbacks.demo_before_model if demo else callbacks.log_before_model

        self.agent = LlmAgent(
            name="agente_base",
            model=self.settings.llm_model,
            instruction="Voce e um assistente que usa as tools disponiveis para resolver a tarefa.",
            tools=TOOLS,
            before_model_callback=before_model,
            after_model_callback=callbacks.log_after_model,
            before_tool_callback=callbacks.log_before_tool,
            after_tool_callback=callbacks.log_after_tool,
        )
        self.runner = InMemoryRunner(agent=self.agent, app_name=_APP)

    async def _responder_async(self, pergunta: str) -> str:
        await self.runner.session_service.create_session(
            app_name=_APP, user_id=_USER, session_id="s1"
        )
        msg = types.Content(role="user", parts=[types.Part(text=pergunta)])
        resposta = ""
        async for event in self.runner.run_async(user_id=_USER, session_id="s1", new_message=msg):
            if event.content and event.content.parts:
                for p in event.content.parts:
                    if p.text:
                        resposta = p.text
        return resposta

    def responder(self, pergunta: str) -> str:
        """Versao sincrona (roda o loop async por baixo)."""
        return asyncio.run(self._responder_async(pergunta))
