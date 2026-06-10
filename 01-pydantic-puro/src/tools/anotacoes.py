"""Tool de exemplo: salvar e ler anotacoes em um arquivo de texto.

Mostra uma tool com EFEITO COLATERAL (mexe em arquivo) e com mais de uma "acao".
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from tools.base import Tool

# Arquivo onde as anotacoes ficam (na raiz do projeto). Esta no .gitignore.
_ARQUIVO = Path("anotacoes.txt")


class AnotacoesArgs(BaseModel):
    acao: Literal["salvar", "ler"] = Field(description="'salvar' grava um texto; 'ler' devolve tudo")
    texto: str = Field(default="", description="Texto a salvar (so usado quando acao='salvar')")


def _anotacoes(args: AnotacoesArgs) -> str:
    if args.acao == "salvar":
        if not args.texto.strip():
            raise ValueError("nada pra salvar: 'texto' veio vazio")
        with _ARQUIVO.open("a", encoding="utf-8") as f:
            f.write(args.texto.strip() + "\n")
        return f"anotacao salva em {_ARQUIVO}"

    # acao == "ler"
    if not _ARQUIVO.exists():
        return "(nenhuma anotacao ainda)"
    return _ARQUIVO.read_text(encoding="utf-8").strip() or "(nenhuma anotacao ainda)"


anotacoes = Tool(
    nome="anotacoes",
    descricao="Salva uma anotacao em arquivo (acao='salvar') ou le todas (acao='ler').",
    modelo_args=AnotacoesArgs,
    funcao=_anotacoes,
)
