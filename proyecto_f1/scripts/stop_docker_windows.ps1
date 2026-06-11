$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $ProjectRoot

docker compose down --remove-orphans

Pop-Location

Write-Host "Docker detenido." -ForegroundColor Green
