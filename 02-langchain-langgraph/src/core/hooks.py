"""Hooks/observabilidade no estilo LangChain — um CallbackHandler.

No projeto de Pydantic puro escrevemos os hooks do zero. No LangChain ja existe
o protocolo de callbacks: voce herda de BaseCallbackHandler e implementa os
eventos que quiser. E o mesmo conceito de before_model/after_tool.

# C#: e como implementar uma interface de eventos / um ILogger que o framework
#     chama em cada etapa. Aqui e onde voce plugaria Langfuse, OpenTelemetry, etc.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler


class HookDeLog(BaseCallbackHandler):
    """Imprime no terminal cada chamada de modelo e de tool."""

    def on_chat_model_start(self, serialized: Any, messages: Any, **kwargs: Any) -> None:
        print("\n>> pensando (chamando o modelo)...")

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        print("<< modelo respondeu")

    def on_tool_start(self, serialized: Any, input_str: str, **kwargs: Any) -> None:
        nome = (serialized or {}).get("name", "tool")
        print(f"   -> usando tool '{nome}' com {input_str}")

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        print(f"   <- tool retornou: {output}")
