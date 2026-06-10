#!/usr/bin/env bash
# setup.sh — mesma coisa do setup.ps1, mas pra Mac/Linux (Google ADK)
#   bash scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."
echo "==> Projeto: Google ADK"
command -v python3 >/dev/null || { echo "Instale o Python 3.10+ primeiro"; exit 1; }
python3 --version
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip >/dev/null
./.venv/bin/python -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
./.venv/bin/python -m pytest -q
echo ""
echo "OK! Para rodar o exemplo:  ./.venv/bin/python src/main.py"
