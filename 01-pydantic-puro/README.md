# 01 — Agente do Zero (Python puro + Pydantic)

O agente **sem framework nenhum**. Aqui você vê *exatamente* como um agente
funciona por dentro: o loop, as ferramentas e os hooks escritos à mão. É o melhor
ponto de partida — depois os frameworks (projetos 02 e 03) fazem isso por você.

## ▶️ Rodar

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1   # instala tudo
powershell -ExecutionPolicy Bypass -File scripts\run.ps1     # roda o exemplo
```
Mac/Linux: `bash scripts/setup.sh` e `./.venv/bin/python src/main.py`.

Sem chave no `.env`, roda em **MODO DEMO** (LLM mockado, offline, de graça).

## 🧠 Como funciona (o loop agêntico)

O coração está em [`src/core/loop.py`](src/core/loop.py). É o ciclo que o curso
ensina na Trilha 1.2:

```
você pergunta
     │
     ▼
┌─► THINK     manda o histórico pro LLM, ele decide o que fazer
│   ACT       se ele pediu uma tool, a gente executa em Python
│   OBSERVE   devolve o resultado da tool pro LLM
└── EVALUATE  repete até o LLM dizer "acabei" (ou bater max_iters)
```

## 🗂️ Mapa dos arquivos

```
src/
├── main.py              # exemplo: monta o agente e faz a pergunta
├── core/
│   ├── config.py        # lê o .env de forma tipada (provedor, chaves, max_iters)
│   ├── llm.py           # cliente do LLM: Anthropic real + DemoClient (mock offline)
│   ├── loop.py          # ★ o loop agêntico (think→act→observe→evaluate)
│   └── hooks.py         # ganchos before_model/after_model/before_tool/after_tool
└── tools/
    ├── base.py          # classe Tool + ToolRegistry (o "dispatcher")
    ├── calculadora.py   # tool de exemplo (matemática segura)
    └── anotacoes.py     # tool de exemplo (salva/lê arquivo)
```

> 🟦 O código tem comentários `# C#:` mapeando os conceitos (Protocol→interface,
> @dataclass→record, etc.). Veja o "Vindo do C#" no [README raiz](../README.md).

## ➕ Adicionar uma ferramenta nova

1. Crie um arquivo em `src/tools/` com um modelo Pydantic (os parâmetros) + uma
   função que recebe esse modelo e retorna `str`.
2. Embrulhe em `Tool(...)` (veja `calculadora.py`).
3. Registre no `main.py`: `agente.adicionar_tool(minha_tool)`.

## 🔌 Usar o Claude de verdade

No `.env`: ponha `LLM_PROVIDER=anthropic` e `ANTHROPIC_API_KEY=sk-ant-...`
(chave em <https://console.anthropic.com>). Rode de novo — agora é o Claude pensando.

## 🌱 Crescer

Veja o `requirements-extra.txt`: tem LangChain, RAG (FAISS/Chroma), MCP, Langfuse,
OpenTelemetry... tudo comentado, agrupado por trilha do curso. Descomente e instale
conforme for precisando. Os **hooks** (`core/hooks.py`) são o lugar natural pra
plugar observabilidade (Langfuse/OTel → Grafana).
