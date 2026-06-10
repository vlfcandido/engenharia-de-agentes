"""O GRAFO do LangGraph — o "loop agentico" virou um grafo de estados.

No projeto de Pydantic puro o loop era um `for` explicito. No LangGraph voce
descreve o fluxo como um GRAFO e a biblioteca roda pra voce:

    START -> [agent] --tem tool_call?--> [tools] -> volta pro [agent]
                 |
                 +--nao--> END

    [agent] = THINK   (chama o modelo)
    [tools] = ACT+OBSERVE (executa as tools e devolve o resultado)

# C#: pense no StateGraph como montar uma state machine / workflow tipado.
#     MessagesState e o "estado" que flui entre os nodes (tipo um record imutavel
#     que cada etapa recebe e devolve atualizado).
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from tools.ferramentas import TOOLS


def construir_grafo(modelo: BaseChatModel) -> CompiledStateGraph:
    """Monta e compila o grafo agentico (agent <-> tools)."""

    # Liga as tools ao modelo: agora ele pode pedir pra usa-las.
    # C#: equivalente a injetar as dependencias que o "cerebro" pode chamar.
    modelo_com_tools = modelo.bind_tools(TOOLS)

    # Node THINK: chama o modelo e devolve a nova mensagem pro estado.
    def node_agente(state: MessagesState) -> dict:
        resposta = modelo_com_tools.invoke(state["messages"])
        return {"messages": [resposta]}

    # Node ACT+OBSERVE: o ToolNode ja executa as tools pedidas e devolve ToolMessages.
    node_tools = ToolNode(TOOLS)

    # Aresta condicional: se a ultima msg pediu tool, vai pra [tools]; senao, acabou.
    # C#: e o "if (response.HasToolCalls) goto tools; else return;"
    def decidir(state: MessagesState) -> str:
        ultima = state["messages"][-1]
        return "tools" if getattr(ultima, "tool_calls", None) else END

    grafo = StateGraph(MessagesState)
    grafo.add_node("agent", node_agente)
    grafo.add_node("tools", node_tools)
    grafo.add_edge(START, "agent")
    grafo.add_conditional_edges("agent", decidir, {"tools": "tools", END: END})
    grafo.add_edge("tools", "agent")
    return grafo.compile()
