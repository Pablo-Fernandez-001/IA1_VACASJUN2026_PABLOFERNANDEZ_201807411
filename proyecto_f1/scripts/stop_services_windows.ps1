$ErrorActionPreference = "SilentlyContinue"

$Ports = 8000, 8001, 8002, 5173
$Connections = Get-NetTCPConnection -LocalPort $Ports -State Listen

if (-not $Connections) {
    Write-Host "No hay servicios de Doctor Byte escuchando en 8000, 8001, 8002 o 5173." -ForegroundColor Green
    exit 0
}

$Connections | ForEach-Object {
    $ProcessId = $_.OwningProcess
    $Process = Get-Process -Id $ProcessId
    Write-Host "Deteniendo puerto $($_.LocalPort) usado por PID $ProcessId ($($Process.ProcessName))" -ForegroundColor Yellow
    Stop-Process -Id $ProcessId -Force
}

Write-Host "Servicios detenidos." -ForegroundColor Green
