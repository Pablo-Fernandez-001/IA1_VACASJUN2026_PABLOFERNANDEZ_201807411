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
    if ($Process.ProcessName -in @("com.docker.backend", "wslrelay")) {
        Write-Host "Saltando puerto $($_.LocalPort): lo administra Docker ($($Process.ProcessName)). Usa .\scripts\stop_docker_windows.ps1 para detener contenedores." -ForegroundColor Cyan
        return
    }
    Write-Host "Deteniendo puerto $($_.LocalPort) usado por PID $ProcessId ($($Process.ProcessName))" -ForegroundColor Yellow
    Stop-Process -Id $ProcessId -Force
}

Write-Host "Servicios detenidos." -ForegroundColor Green
