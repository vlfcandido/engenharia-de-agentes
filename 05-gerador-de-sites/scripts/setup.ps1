# setup.ps1 — instala tudo (05 gerador de sites)  [Windows]
#   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
Write-Host "==> Projeto: 05 gerador de sites" -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "==> Instalando Python via winget..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    Write-Host "!! Reabra o PowerShell e rode o setup de novo." -ForegroundColor Yellow; exit 0
}
python --version
if (-not (Test-Path .venv)) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip | Out-Null
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
& .\.venv\Scripts\python.exe -m pytest -q
Write-Host "OK! rode:  powershell -ExecutionPolicy Bypass -File scripts\run.ps1" -ForegroundColor Green
Write-Host "Depois abra workspace\site\index.html no navegador." -ForegroundColor Green
