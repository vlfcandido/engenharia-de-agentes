"""Tools no estilo ADK — funcoes Python comuns que retornam um dict.

O ADK le a assinatura (com type hints) + a docstring e gera o schema sozinho.
# C#: como um metodo publico tipado que o framework expoe como "ferramenta";
#     os type hints fazem o papel dos tipos do C# (string, etc.).
"""

from __future__ import annotations

import ast
import operator
from pathlib import Path

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


def calculadora(expressao: str) -> dict:
    """Calcula uma expressao matematica simples, ex.: '(2 + 3) * 4'.

    Args:
        expressao: a conta a calcular.
    """
    try:
        arvore = ast.parse(expressao, mode="eval").body
        return {"resultado": str(_avaliar(arvore))}
    except Exception as exc:  # noqa: BLE001
        return {"erro": f"{type(exc).__name__}: {exc}"}


def anotacoes(acao: str, texto: str = "") -> dict:
    """Salva uma anotacao (acao='salvar') ou le todas (acao='ler').

    Args:
        acao: 'salvar' ou 'ler'.
        texto: o texto a salvar (so quando acao='salvar').
    """
    if acao == "salvar":
        if not texto.strip():
            return {"erro": "nada pra salvar: 'texto' veio vazio"}
        with _ARQUIVO.open("a", encoding="utf-8") as f:
            f.write(texto.strip() + "\n")
        return {"status": f"anotacao salva em {_ARQUIVO}"}
    if not _ARQUIVO.exists():
        return {"conteudo": "(nenhuma anotacao ainda)"}
    return {"conteudo": _ARQUIVO.read_text(encoding="utf-8").strip() or "(nenhuma anotacao ainda)"}


TOOLS = [calculadora, anotacoes]
