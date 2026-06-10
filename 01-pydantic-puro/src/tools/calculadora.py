"""Tool de exemplo: calculadora segura.

Mostra o padrao completo de uma tool: modelo Pydantic + funcao + objeto Tool.
"""

from __future__ import annotations

import ast
import operator

from pydantic import BaseModel, Field

from tools.base import Tool

# Operadores permitidos. NAO usamos eval() cru (perigoso) — avaliamos a arvore
# sintatica manualmente, aceitando so matematica. Seguranca eh tema da Trilha 2.4.
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


class CalculadoraArgs(BaseModel):
    expressao: str = Field(
        description="Expressao matematica a calcular, ex.: '(2 + 3) * 4' ou '15 ** 2'"
    )


def _calcular(args: CalculadoraArgs) -> str:
    arvore = ast.parse(args.expressao, mode="eval").body
    resultado = _avaliar(arvore)
    return str(resultado)


calculadora = Tool(
    nome="calculadora",
    descricao="Calcula uma expressao matematica simples e retorna o resultado.",
    modelo_args=CalculadoraArgs,
    funcao=_calcular,
)
