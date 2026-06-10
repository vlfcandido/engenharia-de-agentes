"""Cliente de LLM — a camada que fala com o modelo.

Tudo aqui e provider-agnostico: o loop nao sabe se esta falando com Claude, GPT
ou um mock. Ele so chama `cliente.completar(messages, tools)` e recebe uma
`LLMResponse` normalizada.

Provedores:
    - AnthropicClient : usa o SDK `anthropic` (Claude). Default do curso.
    - DemoClient      : mock offline e deterministico. Roda SEM chave de API,
                        pra voce ver o loop agentico funcionando de gratis.
    - OpenAI / Gemini : stubs comentados. Implemente quando precisar (Trilha 2.1/3.4).

Formato interno das mensagens = formato de "blocos" da Anthropic (role + content
em blocos). Eh um formato so pra todo o projeto; um adapter de OpenAI/Gemini
traduziria de/para esse formato.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from core.config import Settings

# Modelos default por provedor (usados quando settings.llm_model esta vazio).
_MODELO_DEFAULT = {
    "anthropic": "claude-sonnet-4-6",
}


# C#: @dataclass e como um `record` — uma classe que so carrega dados, com
#     construtor/igualdade gerados automaticamente.
@dataclass
class ToolCall:
    """Um pedido do LLM pra usar uma tool."""

    id: str
    nome: str
    args: dict[str, Any]


@dataclass
class LLMResponse:
    """Resposta normalizada do LLM, independente do provedor."""

    texto: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = "end_turn"  # "end_turn" = acabou | "tool_use" = quer usar tools
    usage: dict[str, int] = field(default_factory=dict)
    # Conteudo bruto do assistant, no formato da Anthropic, pra reanexar no historico.
    assistant_content: list[dict[str, Any]] = field(default_factory=list)


# C#: Protocol e uma INTERFACE (ILLMClient). Qualquer classe que tenha um metodo
#     `completar(...)` com essa assinatura "implementa" o contrato — sem precisar
#     herdar explicitamente (duck typing). AnthropicClient e DemoClient cumprem isso.
class LLMClient(Protocol):
    """Contrato que todo provedor implementa."""

    def completar(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], sistema: str = ""
    ) -> LLMResponse: ...


# ---------------------------------------------------------------------------
#  Anthropic (Claude) — provedor real default
# ---------------------------------------------------------------------------
class AnthropicClient:
    def __init__(self, settings: Settings) -> None:
        from anthropic import Anthropic  # import tardio: so carrega se for usar

        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.llm_model or _MODELO_DEFAULT["anthropic"]

    def completar(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], sistema: str = ""
    ) -> LLMResponse:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            messages=messages,
            tools=tools or None,
            system=sistema or None,  # a camada de prompt (instrucoes confiaveis)
        )
        texto = ""
        tool_calls: list[ToolCall] = []
        assistant_content: list[dict[str, Any]] = []
        for bloco in resp.content:
            if bloco.type == "text":
                texto += bloco.text
                assistant_content.append({"type": "text", "text": bloco.text})
            elif bloco.type == "tool_use":
                tool_calls.append(ToolCall(id=bloco.id, nome=bloco.name, args=dict(bloco.input)))
                assistant_content.append(
                    {"type": "tool_use", "id": bloco.id, "name": bloco.name, "input": bloco.input}
                )
        return LLMResponse(
            texto=texto,
            tool_calls=tool_calls,
            stop_reason=resp.stop_reason or "end_turn",
            usage={"input": resp.usage.input_tokens, "output": resp.usage.output_tokens},
            assistant_content=assistant_content,
        )


# ---------------------------------------------------------------------------
#  Demo — mock offline, deterministico, sem custo
# ---------------------------------------------------------------------------
class DemoClient:
    """Simula um modelo "pensando" pra demonstrar o loop SEM chamar API nenhuma.

    Regra: ele conta quantas tools ja rodaram (blocos tool_result no historico) e
    decide o proximo passo. Assim o loop roda varias iteracoes de verdade:
        passo 0 -> usa a calculadora
        passo 1 -> salva o resultado nas anotacoes
        passo 2 -> responde e encerra (end_turn)
    """

    def completar(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], sistema: str = ""
    ) -> LLMResponse:
        # O demo ignora o system prompt (e mockado), mas a assinatura bate com a real.
        resultados = self._tool_results(messages)
        n = len(resultados)
        usage = {"input": 50 + 20 * n, "output": 30}

        if n == 0:
            expr = self._extrair_expressao(messages)
            return self._chamada_tool("calculadora", {"expressao": expr}, usage)

        if n == 1:
            resultado = resultados[0]
            return self._chamada_tool(
                "anotacoes", {"acao": "salvar", "texto": f"Resultado calculado: {resultado}"}, usage
            )

        resultado = resultados[0]
        texto = (
            f"Pronto! O resultado e {resultado} e ja salvei nas suas anotacoes. "
            f"(resposta gerada em MODO DEMO — configure uma chave no .env pra usar um LLM real)"
        )
        return LLMResponse(
            texto=texto,
            stop_reason="end_turn",
            usage=usage,
            assistant_content=[{"type": "text", "text": texto}],
        )

    @staticmethod
    def _chamada_tool(nome: str, args: dict[str, Any], usage: dict[str, int]) -> LLMResponse:
        tool_id = f"demo-{nome}"
        return LLMResponse(
            tool_calls=[ToolCall(id=tool_id, nome=nome, args=args)],
            stop_reason="tool_use",
            usage=usage,
            assistant_content=[{"type": "tool_use", "id": tool_id, "name": nome, "input": args}],
        )

    @staticmethod
    def _tool_results(messages: list[dict[str, Any]]) -> list[str]:
        saidas: list[str] = []
        for msg in messages:
            conteudo = msg.get("content")
            if isinstance(conteudo, list):
                for bloco in conteudo:
                    if isinstance(bloco, dict) and bloco.get("type") == "tool_result":
                        saidas.append(str(bloco.get("content", "")))
        return saidas

    @staticmethod
    def _extrair_expressao(messages: list[dict[str, Any]]) -> str:
        # Pega o texto do primeiro turno do usuario e tenta achar uma conta.
        texto = ""
        for msg in messages:
            if msg.get("role") == "user":
                c = msg.get("content")
                texto = c if isinstance(c, str) else str(c)
                break
        m = re.search(r"[\d\.\s\(\)\+\-\*/%]{3,}", texto)
        return (m.group(0).strip() if m else "(12 * 8) + 5") or "(12 * 8) + 5"


# ---------------------------------------------------------------------------
#  OpenAI / Gemini — implemente quando precisar (Trilha 2.1 / 3.4)
# ---------------------------------------------------------------------------
# class OpenAIClient:
#     def __init__(self, settings: Settings) -> None:
#         from openai import OpenAI            # pip install openai (requirements-extra.txt)
#         self._client = OpenAI(api_key=settings.openai_api_key)
#         self._model = settings.llm_model or "gpt-4o"
#     def completar(self, messages, tools) -> LLMResponse:
#         # Traduza messages/tools pro formato da OpenAI (role/content + tools=[{type:function}]),
#         # chame self._client.chat.completions.create(...), e converta de volta pra LLMResponse.
#         raise NotImplementedError("Implemente o adapter da OpenAI aqui.")


def criar_cliente(settings: Settings) -> LLMClient:
    """Fabrica: escolhe o cliente certo com base no .env."""
    provider = settings.provider_efetivo
    if provider == "anthropic":
        return AnthropicClient(settings)
    # if provider == "openai":
    #     return OpenAIClient(settings)
    return DemoClient()
