Write-Host "Levantando SmartBot con Docker Compose..." -ForegroundColor Cyan
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))
docker compose up --build
