Write-Host "Deteniendo SmartBot..." -ForegroundColor Cyan
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))
docker compose down
