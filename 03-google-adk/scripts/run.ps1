# Roda o exemplo (src\main.py) usando o Python do .venv.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path .venv)) {
    Write-Host "Ambiente nao encontrado. Rode primeiro: scripts\setup.ps1" -ForegroundColor Red
    exit 1
}
& .\.venv\Scripts\python.exe src\main.py
