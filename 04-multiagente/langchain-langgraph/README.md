# 04 — Time multi-agente · LangGraph

Variante **LangGraph** do time planejador/executor/revisor. A arquitetura, a camada de
prompt, a segurança e o A2A estão explicados no **[README do projeto 04](../README.md)**
e em **[SEGURANCA.md](../SEGURANCA.md)** — leia lá primeiro.

## Rodar
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1   # instala + testa
powershell -ExecutionPolicy Bypass -File scripts\run.ps1     # roda o exemplo
```
Mac/Linux: `bash scripts/setup.sh` e `./.venv/bin/python src/main.py`.
Sem chave no `.env` => MODO DEMO (offline).

## O que muda neste variante
Orquestração como `StateGraph` em `src/agents/graph.py` (nós planejar/executar/revisar + aresta condicional de loop). Os agentes são os mesmos do variante Pydantic.
