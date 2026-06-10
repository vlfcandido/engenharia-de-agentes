"""A2A — comunicacao entre agentes.

Os agentes (planejador, executor, revisor) NAO se chamam direto: eles trocam
**mensagens tipadas**. Isso e o coracao de um sistema multi-agente e e o que o
protocolo aberto **A2A (Agent2Agent, do Google)** padroniza pra agentes de
fornecedores diferentes conversarem.

Aqui fazemos uma versao LOCAL e simples (tudo no mesmo processo), mas com o mesmo
formato de envelope. Pra ir cross-process/cross-vendor depois, voce expoe cada
agente como um "servidor A2A" e troca este barramento por chamadas HTTP — a forma
das mensagens continua a mesma.

# C#: pense numa mensagem A2A como um DTO/record que voce poe numa fila (tipo um
#     MediatR/MassTransit). O 'Barramento' abaixo e um bus em memoria.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# Tipos de mensagem que circulam no sistema. Adicione os seus conforme crescer.
TipoMensagem = Literal["objetivo", "plano", "execucao", "veredito"]


class Mensagem(BaseModel):
    """Envelope A2A: quem fala, com quem, que tipo e o conteudo estruturado.

    Os campos espelham o protocolo A2A real (que tem role, parts, taskId, etc.).
    """

    de: str  # agente de origem  (ex.: "planejador")
    para: str  # agente de destino (ex.: "executor")
    tipo: TipoMensagem
    conteudo: dict[str, Any] = Field(default_factory=dict)
    # 'confiavel' marca se o conteudo veio de fonte confiavel (nossos agentes) ou
    # se carrega dados nao-confiaveis (entrada do usuario, web, CRM...). Usado pela
    # camada de seguranca. Veja core/seguranca.py.
    confiavel: bool = True


class Barramento:
    """Bus em memoria que registra o historico de mensagens trocadas (trilha de auditoria).

    Guardar todas as mensagens da observabilidade de graca: voce ve EXATAMENTE o
    que cada agente disse a quem. E o lugar natural pra plugar Langfuse/OTel.
    """

    def __init__(self) -> None:
        self.historico: list[Mensagem] = []

    def enviar(self, msg: Mensagem) -> Mensagem:
        self.historico.append(msg)
        print(f"   [A2A] {msg.de} --{msg.tipo}--> {msg.para}")
        return msg
