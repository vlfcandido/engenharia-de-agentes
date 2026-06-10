#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "==> Projeto: 04 multi-agente — LangGraph"
command -v python3 >/dev/null || { echo "Instale Python 3.10+"; exit 1; }
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip >/dev/null
./.venv/bin/python -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
./.venv/bin/python -m pytest -q
echo "OK! rode: ./.venv/bin/python src/main.py"
