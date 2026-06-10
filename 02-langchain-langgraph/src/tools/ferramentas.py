"""Tools no estilo LangChain — funcoes decoradas com @tool.

Mesmas duas ferramentas dos outros projetos (calculadora + anotacoes), mas aqui
o LangChain gera o schema automaticamente a partir da assinatura + docstring.
"""

from __future__ import annotations

import ast
import operator
from pathlib import Path
from typing import Literal

from langchain_core.tools import tool

# --- calculadora segura (mesma logica dos outros projetos) ------------------
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _avaliar(no: ast.AST) -> float:
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return float(no.value)
    if isinstance(no, ast.BinOp) and type(no.op) in _OPS:
        return _OPS[type(no.op)](_avaliar(no.left), _avaliar(no.right))
    if isinstance(no, ast.UnaryOp) and type(no.op) in _OPS:
        return _OPS[type(no.op)](_avaliar(no.operand))
    raise ValueError("expressao nao permitida (use apenas numeros e + - * / ** %)")


_ARQUIVO = Path("anotacoes.txt")


@tool
def calculadora(expressao: str) -> str:
    """Calcula uma expressao matematica simples, ex.: '(2 + 3) * 4'."""
    arvore = ast.parse(expressao, mode="eval").body
    return str(_avaliar(arvore))


@tool
def anotacoes(acao: Literal["salvar", "ler"], texto: str = "") -> str:
    """Salva uma anotacao em arquivo (acao='salvar') ou le todas (acao='ler')."""
    if acao == "salvar":
        if not texto.strip():
            raise ValueError("nada pra salvar: 'texto' veio vazio")
        with _ARQUIVO.open("a", encoding="utf-8") as f:
            f.write(texto.strip() + "\n")
        return f"anotacao salva em {_ARQUIVO}"
    if not _ARQUIVO.exists():
        return "(nenhuma anotacao ainda)"
    return _ARQUIVO.read_text(encoding="utf-8").strip() or "(nenhuma anotacao ainda)"


TOOLS = [calculadora, anotacoes]
