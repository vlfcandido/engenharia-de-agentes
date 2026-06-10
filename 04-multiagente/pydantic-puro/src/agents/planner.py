"""Agente PLANEJADOR — transforma objetivo em uma lista de passos."""

from __future__ import annotations

from core.llm import LLMClient, extrair_json
from prompts import planner as prompt_planner


class PlannerAgent:
    papel = "planejador"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def planejar(self, objetivo: str, dados_usuario: str = "") -> list[str]:
        prompt = prompt_planner.montar(objetivo, dados_usuario)
        resposta = self.llm.gerar(prompt, papel=self.papel)
        passos = extrair_json(resposta).get("passos", [])
        return [str(p) for p in passos]
