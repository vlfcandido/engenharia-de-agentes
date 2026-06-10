"""Prompt do agente PLANEJADOR.

A camada de prompt fica TODA aqui (separada do codigo) de proposito: voce ajusta
o comportamento do agente mexendo no texto, sem tocar na logica. Pra escalar pra
outro caso (code review, chatbot, CRM...), normalmente voce so troca estes prompts
+ as tools.
"""

from __future__ import annotations

from core.seguranca import montar_prompt

# Prompt de sistema = a "personalidade" e as regras do agente. Versione isto.
SYSTEM = """\
Voce e o PLANEJADOR de um time de agentes de IA.
Seu unico trabalho e transformar um OBJETIVO em um PLANO curto e executavel.

Regras:
- Quebre o objetivo em 2 a 5 passos concretos e em ordem.
- Cada passo deve ser uma acao verificavel (comeca com um verbo).
- NAO execute nada; so planeje.
- Responda SOMENTE em JSON valido, no formato:
  {"passos": ["passo 1", "passo 2", "..."]}
"""


def montar(objetivo: str, dados_usuario: str = "") -> str:
    """Monta o prompt do planejador injetando o objetivo + dados nao-confiaveis."""
    instrucoes = f"{SYSTEM}\n\nOBJETIVO:\n{objetivo}"
    return montar_prompt(instrucoes_confiaveis=instrucoes, dados_nao_confiaveis=dados_usuario)
