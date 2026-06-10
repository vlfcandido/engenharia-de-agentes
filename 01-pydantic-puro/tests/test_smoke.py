"""Smoke tests — validam que a base monta e roda em MODO DEMO, sem chamar API.

Rode com:  pytest -q
"""

from __future__ import annotations

from agents.agente import Agente
from core.config import Settings
from core.hooks import Hooks
from core.llm import DemoClient
from tools.anotacoes import anotacoes
from tools.calculadora import calculadora


def _agente_demo() -> Agente:
    # Forca modo demo (sem chave) pra nao depender de rede/credencial.
    settings = Settings(llm_provider="demo")
    ag = Agente(settings=settings, cliente=DemoClient(), hooks=Hooks())
    ag.adicionar_tool(calculadora).adicionar_tool(anotacoes)
    return ag


def test_calculadora_segura():
    assert calculadora.executar({"expressao": "(12 * 8) + 5"}) == "101.0"


def test_calculadora_rejeita_codigo_perigoso():
    saida, erro = _agente_demo().tools.executar("calculadora", {"expressao": "__import__('os')"})
    assert erro is not None  # nao deixa rodar codigo arbitrario


def test_loop_demo_responde_e_encerra():
    resposta = _agente_demo().responder("Quanto e (12 * 8) + 5? Salve nas anotacoes.")
    assert "101" in resposta
    assert resposta  # terminou com uma resposta de texto


def test_registry_lista_schemas():
    ag = _agente_demo()
    nomes = {s["name"] for s in ag.tools.schemas()}
    assert {"calculadora", "anotacoes"} <= nomes
