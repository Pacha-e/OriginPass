$ErrorActionPreference = 'Stop'
$root = Join-Path $PSScriptRoot 'app'
if (-not (Test-Path (Join-Path $root '.venv\Scripts\python.exe')) -or -not (Test-Path (Join-Path $root '.env'))) { throw 'Primero ejecuta .\Setup-Portatil.ps1 en esta carpeta.' }
Set-Location $root
& docker compose up -d db
if ($LASTEXITCODE -ne 0) { throw 'Abre Docker Desktop e inicia PostgreSQL.' }
Start-Process 'http://127.0.0.1:8000/'
Write-Host 'Servidor local: http://127.0.0.1:8000/ (Ctrl+C para salir)'
& '.\.venv\Scripts\python.exe' manage.py runserver 127.0.0.1:8000 --noreload
