#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "==> Projeto: 05 gerador de sites"
command -v python3 >/dev/null || { echo "Instale Python 3.10+"; exit 1; }
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip >/dev/null
./.venv/bin/python -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
./.venv/bin/python -m pytest -q
echo "OK! rode: ./.venv/bin/python src/main.py   (e abra workspace/site/index.html)"
