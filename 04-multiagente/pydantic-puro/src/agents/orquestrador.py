"""ORQUESTRADOR — coordena planejador -> executor -> revisor via mensagens A2A.

Fluxo:
    1. Planejador transforma o objetivo em um plano.            (A2A: planejador -> executor)
    2. Executor realiza o plano e produz uma saida.             (A2A: executor  -> revisor)
    3. Revisor aprova ou reprova.                               (A2A: revisor   -> executor)
    4. Se reprovou e ainda ha rounds, volta pro executor com o feedback. Repete.

# C#: e um orquestrador/mediator que roteia mensagens entre handlers, com um
#     loop de no maximo `max_rounds` iteracoes (trava de seguranca/custo).
"""

from __future__ import annotations

from agents.executor import ExecutorAgent
from agents.planner import PlannerAgent
from agents.reviewer import ReviewerAgent
from core.a2a import Barramento, Mensagem
from core.config import Settings, settings as settings_global
from core.llm import criar_cliente


class Orquestrador:
    def __init__(self, *, settings: Settings | None = None) -> None:
        self.settings = settings or settings_global
        llm = criar_cliente(self.settings)
        self.planejador = PlannerAgent(llm)
        self.executor = ExecutorAgent(llm)
        self.revisor = ReviewerAgent(llm)
        self.barramento = Barramento()

    def resolver(self, objetivo: str, dados_usuario: str = "") -> dict:
        # 1. PLANEJAR
        print("\n[PLANEJADOR] montando o plano...")
        plano = self.planejador.planejar(objetivo, dados_usuario)
        self.barramento.enviar(
            Mensagem(de="planejador", para="executor", tipo="plano", conteudo={"passos": plano})
        )
        for i, p in enumerate(plano, 1):
            print(f"   plano[{i}] {p}")

        feedback = ""
        for round_ in range(1, self.settings.max_rounds + 1):
            # 2. EXECUTAR
            print(f"\n[EXECUTOR] round {round_} (feedback: {'sim' if feedback else 'nao'})...")
            execucao = self.executor.executar(objetivo, plano, feedback, dados_usuario)
            self.barramento.enviar(
                Mensagem(de="executor", para="revisor", tipo="execucao", conteudo=execucao)
            )
            print(f"   saida: {execucao['saida']}")

            # 3. REVISAR
            print(f"[REVISOR] round {round_} avaliando...")
            veredito = self.revisor.revisar(objetivo, execucao["saida"])
            self.barramento.enviar(
                Mensagem(de="revisor", para="executor", tipo="veredito", conteudo=veredito)
            )

            if veredito["aprovado"]:
                print("   -> APROVADO ✓")
                return {"objetivo": objetivo, "saida": execucao["saida"], "rounds": round_, "aprovado": True}

            print(f"   -> REPROVADO: {veredito['feedback']}")
            feedback = veredito["feedback"]

        # Estourou os rounds sem aprovacao.
        return {"objetivo": objetivo, "saida": execucao["saida"], "rounds": self.settings.max_rounds, "aprovado": False}
