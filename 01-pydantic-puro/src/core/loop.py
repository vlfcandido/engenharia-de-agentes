"""O LOOP AGENTICO — o coracao de qualquer agente.

Eh o ciclo que o curso ensina na Trilha 1.2:  Think -> Act -> Observe -> Evaluate.
Sem framework nenhum, da pra ver exatamente o que acontece:

    1. THINK    : manda o historico pro LLM e ele decide o que fazer.
    2. ACT      : se ele pediu tools, a gente executa em Python.
    3. OBSERVE  : devolve o resultado das tools pro LLM.
    4. EVALUATE : repete ate o LLM dizer "acabei" (end_turn) ou bater o limite.

A trava `max_iters` evita loop infinito (custo/seguranca) — tambem do curso.
Os `hooks` sao disparados em cada etapa pra voce plugar log/observabilidade/guardrails.
"""

from __future__ import annotations

from typing import Any

from core.hooks import Hooks
from core.llm import LLMClient
from tools.base import ToolRegistry


def rodar_loop(
    *,
    cliente: LLMClient,
    tools: ToolRegistry,
    hooks: Hooks,
    pergunta: str,
    sistema: str = "",
    max_iters: int = 10,
) -> str:
    """Roda o loop agentico para uma pergunta e devolve a resposta final em texto.

    `sistema` e o system prompt (a camada de prompt) — as instrucoes CONFIAVEIS
    que guiam o agente, separadas da `pergunta` (que pode conter dados do usuario).
    """

    # Historico de mensagens (formato de blocos da Anthropic). Comeca com o usuario.
    messages: list[dict[str, Any]] = [{"role": "user", "content": pergunta}]
    schemas = tools.schemas()
    resposta_final = ""

    for i in range(1, max_iters + 1):
        # 1. THINK ------------------------------------------------------------
        hooks.emit("before_model", {"iter": i, "messages": messages})
        resp = cliente.completar(messages, schemas, sistema)
        hooks.emit(
            "after_model",
            {"iter": i, "usage": resp.usage, "stop_reason": resp.stop_reason},
        )

        # Reanexa o que o assistant disse/pediu ao historico.
        messages.append({"role": "assistant", "content": resp.assistant_content})

        if resp.texto:
            resposta_final = resp.texto

        # 4. EVALUATE: se nao pediu tool, acabou.
        if resp.stop_reason != "tool_use" or not resp.tool_calls:
            return resposta_final

        # 2. ACT + 3. OBSERVE -------------------------------------------------
        blocos_resultado: list[dict[str, Any]] = []
        for chamada in resp.tool_calls:
            hooks.emit("before_tool", {"name": chamada.nome, "input": chamada.args})
            saida, erro = tools.executar(chamada.nome, chamada.args)
            hooks.emit("after_tool", {"name": chamada.nome, "output": saida, "error": erro})

            blocos_resultado.append(
                {
                    "type": "tool_result",
                    "tool_use_id": chamada.id,
                    "content": erro if erro else saida,
                    "is_error": erro is not None,
                }
            )

        # OBSERVE: os resultados voltam como um turno do usuario.
        messages.append({"role": "user", "content": blocos_resultado})

    # Estourou o limite de iteracoes.
    return resposta_final or f"(parei: atingi o limite de {max_iters} iteracoes)"
