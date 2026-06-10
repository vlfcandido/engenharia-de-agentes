"""Smoke tests do projeto LangGraph — rodam em MODO DEMO (modelo fake, offline)."""

from __future__ import annotations

from agents.agente import Agente
from core.config import Settings
from tools.ferramentas import calculadora


def test_calculadora_tool():
    # @tool vira um objeto; .invoke roda a funcao por baixo.
    assert calculadora.invoke({"expressao": "(12 * 8) + 5"}) == "101.0"


def test_grafo_demo_responde_e_encerra():
    resposta = Agente(settings=Settings(llm_provider="demo")).responder(
        "Quanto e (12 * 8) + 5? Salve nas anotacoes."
    )
    assert "101" in resposta
