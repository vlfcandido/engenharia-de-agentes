"""Escolha do modelo de chat (real ou fake).

- Com ANTHROPIC_API_KEY: usa ChatAnthropic (Claude) de verdade.
- Sem chave (MODO DEMO): usa FakeToolCallingModel, um modelo offline e
  deterministico que emite as mesmas chamadas de tool do exemplo. Assim o grafo
  do LangGraph roda sem custo nenhum, igual ao projeto de Pydantic puro.
"""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from core.config import Settings


class FakeToolCallingModel(BaseChatModel):
    """Modelo fake que simula um agente decidindo usar tools (offline).

    Olha quantas ToolMessages ja existem no historico e decide o proximo passo:
        0 -> chama a calculadora
        1 -> salva o resultado nas anotacoes
        2 -> responde e encerra
    """

    @property
    def _llm_type(self) -> str:
        return "fake-tool-calling"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "FakeToolCallingModel":
        # No fake nao precisamos das tools de verdade — so devolvemos a nos mesmos.
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        resultados = [m for m in messages if isinstance(m, ToolMessage)]
        n = len(resultados)

        if n == 0:
            msg = AIMessage(
                content="",
                tool_calls=[{"name": "calculadora", "args": {"expressao": "(12 * 8) + 5"}, "id": "call-1", "type": "tool_call"}],
            )
        elif n == 1:
            resultado = str(resultados[0].content)
            msg = AIMessage(
                content="",
                tool_calls=[{"name": "anotacoes", "args": {"acao": "salvar", "texto": f"Resultado calculado: {resultado}"}, "id": "call-2", "type": "tool_call"}],
            )
        else:
            resultado = str(resultados[0].content)
            msg = AIMessage(
                content=(
                    f"Pronto! O resultado e {resultado} e ja salvei nas suas anotacoes. "
                    f"(MODO DEMO — configure ANTHROPIC_API_KEY no .env pra usar o Claude real)"
                )
            )
        return ChatResult(generations=[ChatGeneration(message=msg)])


def criar_modelo(settings: Settings) -> BaseChatModel:
    """Fabrica o modelo conforme o .env."""
    if settings.provider_efetivo == "anthropic":
        from langchain_anthropic import ChatAnthropic  # import tardio

        return ChatAnthropic(
            model=settings.llm_model,
            api_key=settings.anthropic_api_key,
            max_tokens=4096,
        )
    return FakeToolCallingModel()
