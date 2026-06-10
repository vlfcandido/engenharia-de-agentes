"""Agente REVISOR/TESTADOR — aprova ou reprova a saida (guardrail final)."""

from __future__ import annotations

from core.llm import LLMClient, extrair_json
from prompts import reviewer as prompt_reviewer


class ReviewerAgent:
    papel = "revisor"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def revisar(self, objetivo: str, saida: str) -> dict:
        prompt = prompt_reviewer.montar(objetivo, saida)
        resposta = self.llm.gerar(prompt, papel=self.papel)
        dados = extrair_json(resposta)
        return {"aprovado": bool(dados.get("aprovado", False)), "feedback": str(dados.get("feedback", ""))}
