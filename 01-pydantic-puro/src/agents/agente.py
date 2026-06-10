"""Agente base — amarra todas as pecas.

Um "agente" aqui e so a combinacao de:
    - um cliente de LLM   (o cerebro)         -> core/llm.py
    - um registro de tools (as maos)          -> tools/
    - hooks               (os sensores/ganchos) -> core/hooks.py
    - o loop              (o ritmo)            -> core/loop.py

Monte um agente, registre as tools que ele pode usar, e chame `.responder(...)`.
"""

from __future__ import annotations

from core.config import Settings, settings as settings_global
from core.hooks import Hooks
from core.llm import LLMClient, criar_cliente
from core.loop import rodar_loop
from prompts import SISTEMA
from tools.base import Tool, ToolRegistry


class Agente:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        cliente: LLMClient | None = None,
        hooks: Hooks | None = None,
        sistema: str = SISTEMA,  # a camada de prompt (system prompt)
    ) -> None:
        self.settings = settings or settings_global
        self.cliente = cliente or criar_cliente(self.settings)
        self.hooks = hooks or Hooks()
        self.tools = ToolRegistry()
        self.sistema = sistema

    def adicionar_tool(self, tool: Tool) -> "Agente":
        """Registra uma tool. Retorna self pra encadear chamadas."""
        self.tools.registrar(tool)
        return self

    def responder(self, pergunta: str) -> str:
        """Roda o loop agentico para uma pergunta e devolve a resposta final."""
        return rodar_loop(
            cliente=self.cliente,
            tools=self.tools,
            hooks=self.hooks,
            pergunta=pergunta,
            sistema=self.sistema,
            max_iters=self.settings.max_iters,
        )
