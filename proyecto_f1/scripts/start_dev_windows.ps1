param(
    [switch]$StopExisting
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$LogDir = Join-Path $ProjectRoot "logs"
$Ports = 8000, 8001, 8002, 5173

function Stop-ProjectPorts {
    $Connections = Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue
    if ($Connections) {
        $Connections | ForEach-Object {
            Write-Host "Liberando puerto $($_.LocalPort) (PID $($_.OwningProcess))" -ForegroundColor Yellow
            Stop-Process -Id $_.OwningProcess -Force
        }
    }
}

function Assert-FreePort {
    param([int]$Port)

    $Connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($Connection) {
        throw "El puerto $Port ya esta en uso. Ejecuta .\scripts\stop_services_windows.ps1 o inicia este script con -StopExisting."
    }
}

function Assert-File {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        throw "No existe $Path. Ejecuta primero .\scripts\setup_windows.ps1."
    }
}

if ($StopExisting) {
    Stop-ProjectPorts
}

$Ports | ForEach-Object { Assert-FreePort $_ }
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$PrologPython = Join-Path $ProjectRoot "backend\prolog_service\.venv\Scripts\python.exe"
$ApiPython = Join-Path $ProjectRoot "backend\api_gateway\.venv\Scripts\python.exe"
$TelegramPython = Join-Path $ProjectRoot "backend\telegram_service\.venv\Scripts\python.exe"

Assert-File $PrologPython
Assert-File $ApiPython
Assert-File $TelegramPython

Start-Process -FilePath $PrologPython `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001") `
    -WorkingDirectory (Join-Path $ProjectRoot "backend\prolog_service") `
    -RedirectStandardOutput (Join-Path $LogDir "prolog-service.out.log") `
    -RedirectStandardError (Join-Path $LogDir "prolog-service.err.log") `
    -WindowStyle Hidden

Start-Process -FilePath $TelegramPython `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8002") `
    -WorkingDirectory (Join-Path $ProjectRoot "backend\telegram_service") `
    -RedirectStandardOutput (Join-Path $LogDir "telegram-service.out.log") `
    -RedirectStandardError (Join-Path $LogDir "telegram-service.err.log") `
    -WindowStyle Hidden

Start-Process -FilePath $ApiPython `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory (Join-Path $ProjectRoot "backend\api_gateway") `
    -RedirectStandardOutput (Join-Path $LogDir "api-gateway.out.log") `
    -RedirectStandardError (Join-Path $LogDir "api-gateway.err.log") `
    -WindowStyle Hidden

Start-Process -FilePath "npm.cmd" `
    -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1") `
    -WorkingDirectory (Join-Path $ProjectRoot "frontend") `
    -RedirectStandardOutput (Join-Path $LogDir "frontend.out.log") `
    -RedirectStandardError (Join-Path $LogDir "frontend.err.log") `
    -WindowStyle Hidden

Write-Host "Servicios iniciando..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort, OwningProcess

Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Logs: $LogDir" -ForegroundColor DarkGray
