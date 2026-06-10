"""Tools (ferramentas) — o que o agente consegue FAZER no mundo.

No curso isso aparece como "skills"/"function calling": cada tool e uma funcao
Python com um schema que descreve seus parametros. O LLM nao executa nada — ele
so PEDE ("quero usar a tool X com esses argumentos") e o nosso codigo executa.

Como criar uma tool nova (3 passos):
    1. Crie um modelo Pydantic descrevendo os parametros (com Field(description=...)).
    2. Crie uma funcao que recebe esse modelo e retorna uma string.
    3. Embrulhe os dois em `Tool(...)` e registre no `ToolRegistry`.

Veja exemplos prontos em calculadora.py e anotacoes.py.
"""

from __future__ import annotations

from typing import Any, Callable

from pydantic import BaseModel


# C#: modelo_args (um BaseModel do Pydantic) e como uma classe/record de DTO com
#     validacao via DataAnnotations. ToolRegistry, mais abaixo, e basicamente um
#     Dictionary<string, Tool> com um dispatcher (switch por nome da tool).
class Tool:
    """Une um schema (modelo Pydantic) a uma funcao Python que o executa."""

    def __init__(
        self,
        nome: str,
        descricao: str,
        modelo_args: type[BaseModel],
        funcao: Callable[[BaseModel], str],
    ) -> None:
        self.nome = nome
        self.descricao = descricao
        self.modelo_args = modelo_args
        self.funcao = funcao

    def schema(self) -> dict[str, Any]:
        """Schema no formato que o provedor de LLM espera (estilo Anthropic).

        O Pydantic gera o JSON Schema dos parametros pra gente de graca.
        """
        return {
            "name": self.nome,
            "description": self.descricao,
            "input_schema": self.modelo_args.model_json_schema(),
        }

    def executar(self, args: dict[str, Any]) -> str:
        """Valida os argumentos com o Pydantic e roda a funcao."""
        validado = self.modelo_args.model_validate(args)
        return self.funcao(validado)


class ToolRegistry:
    """Coleciona as tools e roteia as chamadas do LLM (o "dispatcher").

    Tratamento de erro fica AQUI de proposito: se uma tool quebra, devolvemos
    a mensagem de erro pro LLM em vez de derrubar o programa — assim o agente
    pode tentar se recuperar (padrao do curso).
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def registrar(self, tool: Tool) -> None:
        self._tools[tool.nome] = tool

    def schemas(self) -> list[dict[str, Any]]:
        """Lista de schemas pra mandar pro LLM."""
        return [t.schema() for t in self._tools.values()]

    def executar(self, nome: str, args: dict[str, Any]) -> tuple[str, str | None]:
        """Executa a tool pedida. Retorna (saida, erro). `erro` e None se deu certo."""
        tool = self._tools.get(nome)
        if tool is None:
            return "", f"tool '{nome}' nao existe"
        try:
            return tool.executar(args), None
        except Exception as exc:  # noqa: BLE001 — queremos devolver QUALQUER erro pro LLM
            return "", f"{type(exc).__name__}: {exc}"
