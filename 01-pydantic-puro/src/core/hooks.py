"""Hooks de ciclo de vida do agente.

Esta eh a ideia mais importante da arquitetura pra quem quer evoluir o projeto.
Inspirado nos callbacks do ADK (before_model / after_model) e em A2A: em vez de
espalhar `print`/logging/tracing dentro do loop, o loop apenas DISPARA eventos e
voce PLUGA o que quiser neles, sem tocar no core.

Eventos disponiveis:
    before_model  -> antes de cada chamada ao LLM   (payload: {iter, messages})
    after_model   -> depois da resposta do LLM       (payload: {iter, usage, stop_reason})
    before_tool   -> antes de executar uma tool       (payload: {name, input})
    after_tool    -> depois de executar uma tool      (payload: {name, output, error})

Por que isso importa:
    - Observabilidade: registre um hook que manda os eventos pro Langfuse / OTel
      (-> Grafana/Tempo). O core nao muda nada.
    - Custo: o hook `after_model` aqui ja imprime tokens por iteracao
      (o curso valoriza "token tracking visivel").
    - Guardrails / A2A: um hook `before_tool` pode barrar tools perigosas ou
      encaminhar a chamada pra outro agente.
"""

from __future__ import annotations

from typing import Any, Callable

# Um handler eh so uma funcao que recebe um dicionario de payload.
# C#: Callable[[dict], None] e um delegate `Action<Dictionary<string, object>>`.
Handler = Callable[[dict[str, Any]], None]


class Hooks:
    """Registro simples de callbacks por evento."""

    EVENTOS = ("before_model", "after_model", "before_tool", "after_tool")

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = {e: [] for e in self.EVENTOS}

    def on(self, evento: str, handler: Handler) -> None:
        """Registra um handler para um evento. Ex.: hooks.on("after_tool", f)."""
        if evento not in self._handlers:
            raise ValueError(f"Evento desconhecido: {evento!r}. Use um de {self.EVENTOS}.")
        self._handlers[evento].append(handler)

    def emit(self, evento: str, payload: dict[str, Any]) -> None:
        """Dispara um evento. Chamado pelo loop — voce normalmente nao chama isso."""
        for handler in self._handlers.get(evento, []):
            handler(payload)


def hook_de_log(hooks: Hooks) -> Hooks:
    """Registra hooks padrao que imprimem o que esta acontecendo no terminal.

    Eh isso que faz o MODO DEMO ficar bonito de ver. Troque/remova a vontade.
    """

    def _before_model(p: dict[str, Any]) -> None:
        print(f"\n[iter {p['iter']}] >> pensando (chamando o LLM)...")

    def _after_model(p: dict[str, Any]) -> None:
        uso = p.get("usage") or {}
        tokens = uso.get("input", 0) + uso.get("output", 0)
        print(f"[iter {p['iter']}] << LLM respondeu (stop={p.get('stop_reason')}, ~{tokens} tokens)")

    def _before_tool(p: dict[str, Any]) -> None:
        print(f"   -> usando tool '{p['name']}' com {p['input']}")

    def _after_tool(p: dict[str, Any]) -> None:
        if p.get("error"):
            print(f"   <- tool '{p['name']}' ERRO: {p['error']}")
        else:
            print(f"   <- tool '{p['name']}' retornou: {p['output']}")

    hooks.on("before_model", _before_model)
    hooks.on("after_model", _after_model)
    hooks.on("before_tool", _before_tool)
    hooks.on("after_tool", _after_tool)
    return hooks
