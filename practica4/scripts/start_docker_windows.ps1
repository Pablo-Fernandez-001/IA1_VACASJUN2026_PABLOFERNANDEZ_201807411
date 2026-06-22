$ErrorActionPreference = "Stop"
$Project = Split-Path -Parent $PSScriptRoot
Set-Location $Project

docker compose up --build -d
docker compose ps
Write-Host "RoboMaze: http://localhost:8401" -ForegroundColor Green
Write-Host "Swagger:  http://localhost:8400/docs" -ForegroundColor Cyan
