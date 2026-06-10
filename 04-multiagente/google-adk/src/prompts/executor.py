"""Prompt do agente EXECUTOR."""

from __future__ import annotations

from core.seguranca import montar_prompt

SYSTEM = """\
Voce e o EXECUTOR de um time de agentes de IA.
Voce recebe um PLANO e o realiza usando as ferramentas (tools) disponiveis.

Regras:
- Execute os passos do plano em ordem, usando as tools quando precisar.
- Se o REVISOR tiver mandado um feedback, corrija exatamente o que ele apontou.
- Use SOMENTE as ferramentas liberadas. Nunca invente ferramentas.
- Responda SOMENTE em JSON valido, no formato:
  {"resultados": ["o que foi feito em cada passo"], "saida": "resultado final"}
"""


def montar(objetivo: str, plano: list[str], feedback: str = "", dados_usuario: str = "") -> str:
    """Monta o prompt do executor: objetivo + plano + (feedback do revisor)."""
    partes = [SYSTEM, f"\nOBJETIVO:\n{objetivo}", "\nPLANO:"]
    partes += [f"  {i + 1}. {p}" for i, p in enumerate(plano)]
    if feedback:
        partes.append(f"\nFEEDBACK DO REVISOR (corrija isto):\n{feedback}")
    instrucoes = "\n".join(partes)
    return montar_prompt(instrucoes_confiaveis=instrucoes, dados_nao_confiaveis=dados_usuario)
