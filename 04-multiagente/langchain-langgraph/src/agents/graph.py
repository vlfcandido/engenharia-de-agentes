"""Orquestracao com LangGraph — planejador -> executor -> revisor (com loop-back).

Aqui o multi-agente vira um GRAFO DE ESTADOS. Os MESMOS agentes do projeto de
Pydantic puro (PlannerAgent/ExecutorAgent/ReviewerAgent) sao reaproveitados como
NOS do grafo — o que muda e o motor de orquestracao (LangGraph cuida do fluxo e
do loop condicional revisor -> executor).

# C#: o StateGraph e a state machine; cada no e um handler; a aresta condicional
#     decide se volta pro executor (reprovado) ou termina (aprovado).
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from agents.executor import ExecutorAgent
from agents.planner import PlannerAgent
from agents.reviewer import ReviewerAgent
from core.a2a import Barramento, Mensagem
from core.config import Settings, settings as settings_global
from core.llm import criar_cliente


class Estado(TypedDict, total=False):
    objetivo: str
    dados: str
    plano: list[str]
    saida: str
    feedback: str
    aprovado: bool
    rounds: int
    max_rounds: int


class Orquestrador:
    def __init__(self, *, settings: Settings | None = None) -> None:
        self.settings = settings or settings_global
        llm = criar_cliente(self.settings)
        self.planejador = PlannerAgent(llm)
        self.executor = ExecutorAgent(llm)
        self.revisor = ReviewerAgent(llm)
        self.barramento = Barramento()
        self.grafo = self._montar()

    def _montar(self):
        def no_planejar(estado: Estado) -> Estado:
            print("\n[PLANEJADOR] montando o plano...")
            plano = self.planejador.planejar(estado["objetivo"], estado.get("dados", ""))
            self.barramento.enviar(Mensagem(de="planejador", para="executor", tipo="plano", conteudo={"passos": plano}))
            return {"plano": plano, "rounds": 0}

        def no_executar(estado: Estado) -> Estado:
            r = estado.get("rounds", 0) + 1
            print(f"\n[EXECUTOR] round {r}...")
            execucao = self.executor.executar(
                estado["objetivo"], estado["plano"], estado.get("feedback", ""), estado.get("dados", "")
            )
            self.barramento.enviar(Mensagem(de="executor", para="revisor", tipo="execucao", conteudo=execucao))
            print(f"   saida: {execucao['saida']}")
            return {"saida": execucao["saida"], "rounds": r}

        def no_revisar(estado: Estado) -> Estado:
            print(f"[REVISOR] round {estado['rounds']} avaliando...")
            veredito = self.revisor.revisar(estado["objetivo"], estado["saida"])
            self.barramento.enviar(Mensagem(de="revisor", para="executor", tipo="veredito", conteudo=veredito))
            print("   -> " + ("APROVADO ✓" if veredito["aprovado"] else f"REPROVADO: {veredito['feedback']}"))
            return {"aprovado": veredito["aprovado"], "feedback": veredito["feedback"]}

        # Aresta condicional: reprovou e ainda tem round? volta pro executor; senao acabou.
        def decidir(estado: Estado) -> str:
            if estado["aprovado"] or estado["rounds"] >= estado["max_rounds"]:
                return END
            return "executar"

        g = StateGraph(Estado)
        g.add_node("planejar", no_planejar)
        g.add_node("executar", no_executar)
        g.add_node("revisar", no_revisar)
        g.add_edge(START, "planejar")
        g.add_edge("planejar", "executar")
        g.add_edge("executar", "revisar")
        g.add_conditional_edges("revisar", decidir, {"executar": "executar", END: END})
        return g.compile()

    def resolver(self, objetivo: str, dados_usuario: str = "") -> dict:
        estado_final = self.grafo.invoke(
            {"objetivo": objetivo, "dados": dados_usuario, "max_rounds": self.settings.max_rounds}
        )
        return {
            "objetivo": objetivo,
            "saida": estado_final.get("saida", ""),
            "rounds": estado_final.get("rounds", 0),
            "aprovado": estado_final.get("aprovado", False),
        }
