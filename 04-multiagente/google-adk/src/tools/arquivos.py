"""Tool de exemplo COM SANDBOX — escreve arquivos so dentro de ./workspace.

Seguranca: o executor pode gerar arquivos, mas NUNCA fora da pasta workspace/.
Isso impede um plano malicioso de escrever em C:\\Windows ou sobrescrever codigo.

# C#: e o mesmo cuidado de validar Path.GetFullPath e conferir se esta dentro do
#     diretorio permitido antes de qualquer File.WriteAllText.
"""

from __future__ import annotations

from pathlib import Path

# A "jaula": tudo que a tool escreve fica aqui dentro.
_WORKSPACE = Path("workspace").resolve()


def escrever_arquivo(nome: str, conteudo: str) -> str:
    """Escreve `conteudo` em workspace/<nome>. Bloqueia tentativas de sair da pasta."""
    _WORKSPACE.mkdir(exist_ok=True)
    destino = (_WORKSPACE / nome).resolve()

    # Trava de sandbox: o caminho final TEM que estar dentro do workspace.
    if not str(destino).startswith(str(_WORKSPACE)):
        raise PermissionError(f"bloqueado: '{nome}' tenta escrever fora do sandbox")

    destino.write_text(conteudo, encoding="utf-8")
    return f"arquivo salvo em workspace/{nome}"
