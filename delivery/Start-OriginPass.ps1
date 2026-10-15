$ErrorActionPreference = 'Stop'
# The app sits in app\ beside this script inside the extracted ZIP, and one
# folder up when the script runs from delivery\ in a clone of the repository.
$root = Join-Path $PSScriptRoot 'app'
$composeArgs = @()
if (Test-Path (Join-Path $root 'manage.py')) { $composeArgs = @('-f', (Join-Path $PSScriptRoot 'docker-compose.kit.yml'), '-p', 'originpass-kit') }
if (-not (Test-Path (Join-Path $root 'manage.py'))) { $root = Split-Path $PSScriptRoot -Parent }
if (-not (Test-Path (Join-Path $root '.venv\Scripts\python.exe')) -or -not (Test-Path (Join-Path $root '.env'))) { throw 'Primero ejecuta Setup-Portatil.ps1, en la misma carpeta que este script.' }
Set-Location $root
& docker compose @composeArgs up -d --wait --wait-timeout 90 db
if ($LASTEXITCODE -ne 0) { throw 'Abre Docker Desktop e inicia PostgreSQL.' }
& '.\.venv\Scripts\python.exe' manage.py migrate --check
if ($LASTEXITCODE -ne 0) { throw 'Hay migraciones pendientes. Ejecuta Setup-Portatil.ps1.' }
& '.\.venv\Scripts\python.exe' (Join-Path $PSScriptRoot 'demo_links.py')
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron generar los enlaces de demostracion.' }
Write-Host 'Servidor local: http://127.0.0.1:8000/ (Ctrl+C para salir)'
Write-Host 'Cuando aparezca Starting development server, abre ABRIR-KIT.html o la direccion anterior.'
& '.\.venv\Scripts\python.exe' manage.py runserver 127.0.0.1:8000 --noreload
