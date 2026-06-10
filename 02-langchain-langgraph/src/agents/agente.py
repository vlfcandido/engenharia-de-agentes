"""Agente — amarra modelo + grafo + hooks (mesma ideia dos outros projetos)."""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from core.config import Settings, settings as settings_global
from core.graph import construir_grafo
from core.hooks import HookDeLog
from core.model import criar_modelo
from prompts import SISTEMA


class Agente:
    def __init__(self, *, settings: Settings | None = None) -> None:
        self.settings = settings or settings_global
        self.modelo = criar_modelo(self.settings)
        self.grafo = construir_grafo(self.modelo)

    def responder(self, pergunta: str) -> str:
        """Roda o grafo e devolve o texto da ultima mensagem do assistente."""
        # recursion_limit limita as voltas do grafo (a trava max_iters daqui).
        config = {"callbacks": [HookDeLog()], "recursion_limit": self.settings.max_iters * 2}
        # A camada de prompt entra como SystemMessage (instrucoes confiaveis), antes
        # da pergunta do usuario.
        mensagens = [SystemMessage(content=SISTEMA), HumanMessage(content=pergunta)]
        estado_final = self.grafo.invoke({"messages": mensagens}, config=config)

        # A resposta e a ultima AIMessage com texto.
        for msg in reversed(estado_final["messages"]):
            if isinstance(msg, AIMessage) and isinstance(msg.content, str) and msg.content.strip():
                return msg.content
        return ""
