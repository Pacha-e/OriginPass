$ErrorActionPreference = 'Stop'
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3.12 (Join-Path $PSScriptRoot 'verify_kit.py') $PSScriptRoot
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python (Join-Path $PSScriptRoot 'verify_kit.py') $PSScriptRoot
} else { throw 'Instala Python 3.12 para verificar el kit.' }
if ($LASTEXITCODE -ne 0) { throw 'El kit esta incompleto o algun archivo cambio. Extrae de nuevo el ZIP verificado.' }
