$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Ensure-Venv {
    param(
        [string]$ServicePath
    )

    $FullPath = Join-Path $ProjectRoot $ServicePath
    $PythonExe = Join-Path $FullPath ".venv\Scripts\python.exe"

    if (-not (Test-Path $PythonExe)) {
        Write-Host "Creando entorno virtual en $ServicePath" -ForegroundColor Cyan
        Push-Location $FullPath
        python -m venv .venv
        Pop-Location
    }
    else {
        Write-Host "Entorno virtual ya existe en $ServicePath" -ForegroundColor DarkGray
    }

    Write-Host "Instalando dependencias de $ServicePath" -ForegroundColor Cyan
    Push-Location $FullPath
    & $PythonExe -m pip install -r requirements.txt
    Pop-Location
}

Push-Location $ProjectRoot

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Archivo .env creado desde .env.example" -ForegroundColor Green
}
else {
    Write-Host "Archivo .env ya existe" -ForegroundColor DarkGray
}

Ensure-Venv "backend\prolog_service"
Ensure-Venv "backend\api_gateway"
Ensure-Venv "backend\telegram_service"

Write-Host "Instalando dependencias del frontend" -ForegroundColor Cyan
Push-Location (Join-Path $ProjectRoot "frontend")
npm install
Pop-Location

Pop-Location

Write-Host "Setup finalizado. Para iniciar: .\scripts\start_dev_windows.ps1" -ForegroundColor Green
