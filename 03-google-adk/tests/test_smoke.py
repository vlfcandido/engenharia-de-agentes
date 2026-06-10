"""Smoke tests do projeto ADK — rodam em MODO DEMO (before_model scriptado)."""

from __future__ import annotations

import warnings

warnings.filterwarnings("ignore", message=".*JSON_SCHEMA_FOR_FUNC_DECL.*")

from agents.agente import Agente  # noqa: E402
from core.config import Settings  # noqa: E402
from tools.ferramentas import calculadora  # noqa: E402


def test_calculadora_tool():
    assert calculadora("(12 * 8) + 5") == {"resultado": "101.0"}


def test_calculadora_rejeita_codigo():
    assert "erro" in calculadora("__import__('os')")


def test_agente_demo_responde():
    resposta = Agente(settings=Settings(llm_provider="demo")).responder(
        "Quanto e (12 * 8) + 5? Salve nas anotacoes."
    )
    assert "101" in resposta
