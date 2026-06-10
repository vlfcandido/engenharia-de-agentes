$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path .venv)) { Write-Host "Rode antes: scripts\setup.ps1" -ForegroundColor Red; exit 1 }
& .\.venv\Scripts\python.exe src\main.py
