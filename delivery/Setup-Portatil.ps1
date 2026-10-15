$ErrorActionPreference = 'Stop'
$root = Join-Path $PSScriptRoot 'app'
if (-not (Test-Path (Join-Path $root 'manage.py'))) { throw 'No se encontro app/manage.py; extrae TODO el ZIP primero.' }
Set-Location $root
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Instala/inicia Docker Desktop, habilita Linux containers y repite este script.' }
& docker info --format '{{.ServerVersion}}' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop no responde. Abre Docker Desktop y repite el script.' }
& docker compose up -d db
if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar PostgreSQL. Verifica que el puerto 5432 este libre.' }
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    if (Get-Command py -ErrorAction SilentlyContinue) { & py -3.12 -m venv .venv }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { & python -m venv .venv }
    else { throw 'Instala Python 3.12 para Windows (con Add to PATH), luego repite.' }
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno Python. Usa Python 3.12.' }
}
$python = Join-Path $root '.venv\Scripts\python.exe'
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Fallo pip install; verifica red y Python 3.12.' }
if (-not (Test-Path '.env')) {
    $key = & $python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    if ($LASTEXITCODE -ne 0 -or -not $key) { throw 'No se pudo generar SECRET_KEY.' }
    $sample = [IO.File]::ReadAllText((Join-Path $root '.env.example'))
    if (-not $sample.Contains('SECRET_KEY=replace-me')) { throw 'Plantilla de entorno inesperada; no se creo .env.' }
    $sample = $sample.Replace('SECRET_KEY=replace-me', ('SECRET_KEY=' + $key))
    [IO.File]::WriteAllText((Join-Path $root '.env'), $sample, [Text.UTF8Encoding]::new($false))
    Write-Host 'Configuracion local nueva creada (no se imprime la clave).'
}
& $python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron aplicar migraciones. Revisa PostgreSQL y .env.' }
& $python manage.py seed_demo
if ($LASTEXITCODE -ne 0) { throw 'Fallo la carga de datos DEMO; NO la ejecutes en produccion.' }
& $python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django check fallo.' }
& $python manage.py verify_integrity
if ($LASTEXITCODE -ne 0) { throw 'Fallaron las cadenas de integridad.' }
Write-Host 'Preparacion local terminada. Para presentar: .\Start-OriginPass.ps1 desde la carpeta extraida.'
