"""Callbacks do ADK = os "hooks" de ciclo de vida.

O ADK ja tem ganchos nativos (e essa foi a razao de escolher ele aqui):
    before_model_callback / after_model_callback   -> em volta da chamada ao LLM
    before_tool_callback  / after_tool_callback     -> em volta de cada tool

# C#: sao eventos/delegates que o framework chama nos momentos certos — como
#     middlewares de um pipeline (ASP.NET) ou um ILogger plugado no fluxo.
#     E aqui que voce plugaria Langfuse / OpenTelemetry depois.

Alem de logar, mostramos como o before_model pode SUBSTITUIR a resposta do LLM:
em MODO DEMO o `demo_before_model` devolve um LlmResponse scriptado e o Gemini
nem e chamado (roda offline, de graca).
"""

from __future__ import annotations

from typing import Any, Optional

from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

# ----------------------------------------------------------------------------
#  Hooks de LOG (usados sempre — em modo real e em modo demo)
# ----------------------------------------------------------------------------


def log_after_model(callback_context: Any, llm_response: LlmResponse) -> None:
    parts = (llm_response.content.parts if llm_response.content else None) or []
    pediu_tool = any(getattr(p, "function_call", None) for p in parts)
    print(f"   << modelo respondeu (quer_tool={pediu_tool})")


def log_before_tool(tool: Any, args: dict, tool_context: Any) -> None:
    print(f"   -> usando tool '{tool.name}' com {args}")


def log_after_tool(tool: Any, args: dict, tool_context: Any, tool_response: Any) -> None:
    print(f"   <- tool '{tool.name}' retornou: {tool_response}")


# ----------------------------------------------------------------------------
#  Driver DEMO — substitui o Gemini por respostas scriptadas (offline)
# ----------------------------------------------------------------------------


def _respostas_de_tools(llm_request: LlmRequest) -> list[dict]:
    """Junta os resultados de tools que ja voltaram, em ordem."""
    saidas: list[dict] = []
    for content in llm_request.contents:
        for part in (content.parts or []):
            fr = getattr(part, "function_response", None)
            if fr is not None:
                saidas.append(dict(fr.response or {}))
    return saidas


def _fc(nome: str, args: dict) -> LlmResponse:
    fc = types.FunctionCall(name=nome, args=args)
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(function_call=fc)]))


def _texto(t: str) -> LlmResponse:
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=t)]))


def demo_before_model(callback_context: Any, llm_request: LlmRequest) -> Optional[LlmResponse]:
    """Simula o raciocinio do modelo SEM chamar a API (MODO DEMO).

    Retornar um LlmResponse faz o ADK PULAR a chamada real ao Gemini.
    Retornar None deixaria seguir pro modelo de verdade.
    """
    resultados = _respostas_de_tools(llm_request)
    n = len(resultados)
    print(f"\n>> pensando (DEMO, passo {n})...")

    if n == 0:
        return _fc("calculadora", {"expressao": "(12 * 8) + 5"})
    if n == 1:
        valor = resultados[0].get("resultado", "?")
        return _fc("anotacoes", {"acao": "salvar", "texto": f"Resultado calculado: {valor}"})

    valor = resultados[0].get("resultado", "?")
    return _texto(
        f"Pronto! O resultado e {valor} e ja salvei nas suas anotacoes. "
        f"(MODO DEMO — configure GOOGLE_API_KEY no .env pra usar o Gemini real)"
    )


def log_before_model(callback_context: Any, llm_request: LlmRequest) -> None:
    """Em modo real, so loga (deixa a chamada seguir pro Gemini)."""
    print("\n>> pensando (chamando o Gemini)...")
