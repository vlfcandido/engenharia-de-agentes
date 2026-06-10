# ============================================================================
#  setup.ps1 — instala TUDO e deixa pronto pra rodar (Pydantic puro)  [Windows]
#  Rode no PowerShell, dentro da pasta do projeto:
#      powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
#  (o -ExecutionPolicy Bypass evita o bloqueio padrao do Windows a scripts)
# ============================================================================
$ErrorActionPreference = "Stop"

# Vai pra raiz do projeto (a pasta acima de \scripts).
Set-Location (Split-Path $PSScriptRoot -Parent)
Write-Host "==> Projeto: Pydantic puro" -ForegroundColor Cyan

# 1. Python 3.10+ — se nao existir, instala via winget.
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "==> Python nao encontrado. Instalando via winget..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    Write-Host "!! Feche e reabra o PowerShell e rode o setup de novo." -ForegroundColor Yellow
    exit 0
}
python --version

# 2. Cria o ambiente virtual (.venv) — uma "caixa" isolada de dependencias.
#    C#: pense no .venv como um diretorio bin/ + packages isolados por projeto,
#        parecido com o que o NuGet restaura por solucao.
if (-not (Test-Path .venv)) {
    Write-Host "==> Criando ambiente virtual (.venv)..."
    python -m venv .venv
}

# 3. Instala as dependencias do requirements.txt dentro do .venv.
Write-Host "==> Instalando dependencias..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip | Out-Null
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 4. Cria o .env a partir do exemplo (so se ainda nao existir).
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "==> Criei o .env (edite pra por suas chaves; sem chave roda em MODO DEMO)."
}

# 5. Roda os testes pra provar que esta tudo de pe.
Write-Host "==> Rodando smoke tests..."
& .\.venv\Scripts\python.exe -m pytest -q

Write-Host ""
Write-Host "OK! Tudo pronto. Para rodar o exemplo:" -ForegroundColor Green
Write-Host "    powershell -ExecutionPolicy Bypass -File scripts\run.ps1" -ForegroundColor Green
