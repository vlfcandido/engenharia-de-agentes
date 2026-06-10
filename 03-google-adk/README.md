# 03 — Agente com Google ADK

O **mesmo agente** dos projetos 01 e 02, agora no **Agent Development Kit** do
Google. O ADK foi escolhido aqui por causa dos **callbacks nativos** de ciclo de
vida (`before_model`, `after_model`, `before_tool`, `after_tool`) — os "hooks" já
vêm de fábrica e são ótimos pra observabilidade e controle.

## ▶️ Rodar

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
powershell -ExecutionPolicy Bypass -File scripts\run.ps1
```
Mac/Linux: `bash scripts/setup.sh` e `./.venv/bin/python src/main.py`.

Sem `GOOGLE_API_KEY` no `.env`, roda em **MODO DEMO**: um `before_model_callback`
*scriptado* simula as decisões do Gemini **offline** (as tools rodam de verdade —
só o "raciocínio" é simulado). É também uma ótima demonstração de como um callback
pode **substituir** a chamada ao modelo.

## 🧠 Como funciona

No ADK você descreve um `LlmAgent` (cérebro + tools + callbacks) e o **Runner**
toca o loop pra você. Os callbacks são chamados em cada etapa:

```
[before_model] ─► (Gemini decide) ─► [after_model]
                                          │ pediu tool?
                            [before_tool] ─► (executa) ─► [after_tool] ─► volta
```

Tudo está em:
- [`src/core/callbacks.py`](src/core/callbacks.py) — os hooks de log **e** o driver
  `demo_before_model` (offline).
- [`src/agents/agente.py`](src/agents/agente.py) — monta o `LlmAgent` + `InMemoryRunner`.

> 🟦 *Vindo do C#:* os callbacks do ADK são como **middlewares de um pipeline**
> (estilo ASP.NET) ou *delegates* que o framework chama nos momentos certos.

## 🗂️ Mapa dos arquivos

```
src/
├── main.py                 # exemplo: faz a pergunta
├── core/
│   ├── config.py           # lê o .env
│   └── callbacks.py        # ★ hooks (before/after model+tool) + driver demo offline
├── tools/
│   └── ferramentas.py      # calculadora + anotacoes (funções comuns; ADK gera o schema)
└── agents/
    └── agente.py           # LlmAgent + InMemoryRunner + responder()
```

## 🔌 Usar o Gemini de verdade (chave grátis)

1. Pegue uma chave **gratuita** em <https://aistudio.google.com/apikey>.
2. No `.env`: `LLM_PROVIDER=gemini` e `GOOGLE_API_KEY=...`.
3. Rode de novo — agora é o Gemini decidindo, e os callbacks de log mostram cada passo.

## 🌱 Crescer

O ADK tem sub-agentes, *sessions* persistentes, *planners* e integra com Vertex AI
(Trilhas 4–6). Plugue Langfuse/OpenTelemetry dentro dos callbacks de
`core/callbacks.py` pra mandar traces pro Grafana.
