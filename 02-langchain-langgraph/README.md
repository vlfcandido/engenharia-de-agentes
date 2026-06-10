# 02 — Agente com LangChain + LangGraph

O **mesmo agente** do projeto 01, mas usando o ecossistema mais popular do mercado.
Aqui o "loop" vira um **grafo de estados** (LangGraph) e as ferramentas usam o
decorator `@tool` do LangChain. Compare com o `01` pra ver o que o framework
automatiza pra você.

## ▶️ Rodar

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
powershell -ExecutionPolicy Bypass -File scripts\run.ps1
```
Mac/Linux: `bash scripts/setup.sh` e `./.venv/bin/python src/main.py`.

Sem `ANTHROPIC_API_KEY` no `.env`, roda em **MODO DEMO** com um modelo *fake*
offline (em `core/model.py`) que emite as mesmas chamadas de tool do exemplo.

## 🧠 Como funciona (o grafo)

O loop do projeto 01 vira este grafo, em [`src/core/graph.py`](src/core/graph.py):

```
START ─► [agent] ──tem tool_call?──► [tools] ─┐
              ▲          │ não                 │
              └──────────┘ END                 │
              └───────────────────────────────┘  (volta pro agent)

[agent] = THINK         (chama o modelo)
[tools] = ACT + OBSERVE (ToolNode executa as tools e devolve o resultado)
```

> 🟦 *Vindo do C#:* o `StateGraph` é como montar uma **state machine / workflow**
> tipado; o `MessagesState` é o estado (um record) que flui entre os nós.

## 🗂️ Mapa dos arquivos

```
src/
├── main.py                 # exemplo: faz a pergunta
├── core/
│   ├── config.py           # lê o .env
│   ├── model.py            # ChatAnthropic (real) ou FakeToolCallingModel (demo)
│   ├── graph.py            # ★ o grafo agêntico (agent ⇄ tools)
│   └── hooks.py            # HookDeLog = um BaseCallbackHandler do LangChain
├── tools/
│   └── ferramentas.py      # calculadora + anotacoes com @tool
└── agents/
    └── agente.py           # monta modelo + grafo + hooks e roda
```

## 🔌 Usar o Claude de verdade

No `.env`: `LLM_PROVIDER=anthropic` e `ANTHROPIC_API_KEY=sk-ant-...`. Quer trocar
de provedor? Instale outro pacote `langchain-*` (ex.: `langchain-openai`) e troque
a importação em `core/model.py`.

## 🌱 Crescer

LangGraph dá *checkpoints* (memória), *streaming* e grafos complexos
(supervisor/multi-agente) — Trilhas 3 e 4. Observabilidade sai de graça com
**LangSmith**: ponha `LANGCHAIN_TRACING_V2=true` e `LANGCHAIN_API_KEY` no `.env`.
