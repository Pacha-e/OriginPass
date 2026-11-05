<#
.SYNOPSIS
Runs the OriginPass verification gates in order and stops at the first failure.

.DESCRIPTION
Gates, run from the repository root:
  1. ruff check .
  2. ruff format --check .
  3. manage.py makemigrations --check --dry-run
  4. manage.py test --noinput

.PARAMETER DatabaseUrl
PostgreSQL connection string, passed to the process as DATABASE_URL. It is never printed.

.PARAMETER Python
Interpreter of the project virtual environment.

.EXAMPLE
powershell -NoProfile -ExecutionPolicy Bypass -File agentes\flujo\verificar.ps1 -DatabaseUrl "postgresql://user:pass@127.0.0.1:55432/originpass"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$DatabaseUrl,

    [string]$Python = 'D:\OriginPass-D4-orq\venv\Scripts\python.exe'
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$previousDatabaseUrl = $env:DATABASE_URL
$previousSecretKey = $env:SECRET_KEY

function Invoke-Gate {
    param(
        [string]$Title,
        [scriptblock]$Command
    )
    Write-Host ('== {0} ==' -f $Title)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw ('gate failed: {0} (exit code {1})' -f $Title, $LASTEXITCODE)
    }
}

try {
    if (-not (Test-Path -LiteralPath $Python)) {
        throw ('Python interpreter not found: {0}' -f $Python)
    }

    $env:DATABASE_URL = $DatabaseUrl
    if (-not $env:SECRET_KEY) {
        $env:SECRET_KEY = 'test-only-not-a-secret'
    }

    Push-Location -LiteralPath $repoRoot
    try {
        Invoke-Gate -Title '1/4 ruff check' -Command { & $Python -m ruff check . }
        Invoke-Gate -Title '2/4 ruff format --check' -Command { & $Python -m ruff format --check . }
        Invoke-Gate -Title '3/4 makemigrations --check --dry-run' -Command { & $Python manage.py makemigrations --check --dry-run }
        Invoke-Gate -Title '4/4 manage.py test --noinput' -Command { & $Python manage.py test --noinput }
    }
    finally {
        Pop-Location
    }

    Write-Host 'All verification gates passed.'
    exit 0
}
catch {
    Write-Host ('FAILED: {0}' -f $_.Exception.Message)
    exit 1
}
finally {
    $env:DATABASE_URL = $previousDatabaseUrl
    $env:SECRET_KEY = $previousSecretKey
}