$ErrorActionPreference = 'Stop'
# The app sits in app\ beside this script inside the extracted ZIP, and one
# folder up when the script runs from delivery\ in a clone of the repository.
$root = Join-Path $PSScriptRoot 'app'
$packaged = Test-Path (Join-Path $root 'manage.py')
$composeArgs = @()
if ($packaged) { $composeArgs = @('-f', (Join-Path $PSScriptRoot 'docker-compose.kit.yml'), '-p', 'originpass-kit') }
if (-not (Test-Path (Join-Path $root 'manage.py'))) { $root = Split-Path $PSScriptRoot -Parent }
if (-not (Test-Path (Join-Path $root 'manage.py'))) { throw 'No se encontro manage.py: extrae TODO el ZIP, o ejecuta este script desde delivery\ dentro del repositorio clonado.' }
Set-Location $root
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Instala/inicia Docker Desktop, habilita Linux containers y repite este script.' }
& docker info --format '{{.ServerVersion}}' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop no responde. Abre Docker Desktop y repite el script.' }
if ($packaged -and -not (Test-Path '.env')) {
    $kitVolumes = @(& docker volume ls --format '{{.Name}}')
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron comprobar los volumenes locales de Docker.' }
    if ($kitVolumes -contains 'originpass-kit_pgdata') { throw 'Ya existe la base del kit en este PC. Usa la carpeta preparada que conserva su .env; no generes otra clave para esa base.' }
}
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
    if ($packaged) { $sample = $sample.Replace('localhost:5432/originpass', 'localhost:55432/originpass') }
    [IO.File]::WriteAllText((Join-Path $root '.env'), $sample, [Text.UTF8Encoding]::new($false))
    Write-Host 'Configuracion local nueva creada (no se imprime la clave).'
}
if ($packaged -and -not ([IO.File]::ReadAllText((Join-Path $root '.env'))).Contains('localhost:55432/originpass')) { throw 'Este kit requiere su base local aislada en el puerto 55432. Usa una extraccion nueva o la carpeta ya preparada de este kit.' }
& docker compose @composeArgs up -d --wait --wait-timeout 90 db
if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar PostgreSQL. Verifica Docker y el puerto local de la base.' }
& $python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron aplicar migraciones. Revisa PostgreSQL y .env.' }
& $python manage.py seed_demo
if ($LASTEXITCODE -ne 0) { throw 'Fallo la carga de datos DEMO; NO la ejecutes en produccion.' }
& $python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django check fallo.' }
& $python manage.py verify_integrity
if ($LASTEXITCODE -ne 0) { throw 'Fallaron las cadenas de integridad.' }
$linksScript = Join-Path $PSScriptRoot 'demo_links.py'
& $python $linksScript
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron preparar los enlaces de demostracion.' }
Write-Host 'Preparacion local terminada. Para presentar: Start-OriginPass.ps1, en la misma carpeta que este script.'
