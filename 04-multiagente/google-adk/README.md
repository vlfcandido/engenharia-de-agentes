# 04 — Time multi-agente · Google ADK

Variante **Google ADK** do time planejador/executor/revisor. A arquitetura, a camada de
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
Cada papel é um `LlmAgent` real do ADK rodado via `Runner` (`src/core/llm.py`); em demo, um `before_model_callback` scriptado responde offline. Provedor real: Gemini (chave grátis no AI Studio).
