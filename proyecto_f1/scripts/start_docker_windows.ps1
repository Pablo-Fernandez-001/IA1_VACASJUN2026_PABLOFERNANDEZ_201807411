$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$DevStopScript = Join-Path $PSScriptRoot "stop_services_windows.ps1"

function Wait-Url {
    param(
        [string]$Name,
        [string]$Url,
        [int]$Attempts = 45
    )

    for ($Index = 1; $Index -le $Attempts; $Index++) {
        try {
            $Response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($Response.StatusCode -ge 200 -and $Response.StatusCode -lt 500) {
                Write-Host "$Name listo: $Url" -ForegroundColor Green
                return
            }
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    throw "$Name no respondio a tiempo en $Url. Revisa: docker compose logs"
}

function Invoke-NativeCommand {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    $PreviousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $Output = & $FilePath @Arguments 2>&1
        $ExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $PreviousPreference
    }

    [pscustomobject]@{
        ExitCode = $ExitCode
        Output = $Output
    }
}

function Get-EnvValue {
    param(
        [string]$Name,
        [string]$DefaultValue = ""
    )

    $Line = Get-Content ".env" -ErrorAction SilentlyContinue |
        Where-Object { $_ -match "^$Name=" } |
        Select-Object -First 1

    if (-not $Line) {
        return $DefaultValue
    }

    $Value = ($Line -replace "^$Name=", "").Trim()
    if (-not $Value) {
        return $DefaultValue
    }

    return $Value
}

Push-Location $ProjectRoot

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Archivo .env creado desde .env.example" -ForegroundColor Green
}

$FrontendPort = Get-EnvValue "FRONTEND_PORT" "8081"

Write-Host "Verificando Docker Desktop..." -ForegroundColor Cyan
$DockerInfo = Invoke-NativeCommand "docker" @("info")
if ($DockerInfo.ExitCode -ne 0) {
    Write-Host ($DockerInfo.Output -join [Environment]::NewLine) -ForegroundColor Red
    Write-Host "Docker Desktop no esta iniciado o el motor Linux no esta disponible. Abre Docker Desktop y espera a que diga 'Docker is running'." -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Limpiando contenedores anteriores..." -ForegroundColor Cyan
$ComposeDown = Invoke-NativeCommand "docker" @("compose", "down", "--remove-orphans")
Write-Host ($ComposeDown.Output -join [Environment]::NewLine)
if ($ComposeDown.ExitCode -ne 0) {
    Write-Host "docker compose down fallo. Revisa que Docker Desktop este corriendo." -ForegroundColor Red
    Pop-Location
    exit 1
}

if (Test-Path $DevStopScript) {
    & $DevStopScript
}

Write-Host "Construyendo y levantando Doctor Byte con Docker..." -ForegroundColor Cyan
$ComposeUp = Invoke-NativeCommand "docker" @("compose", "up", "-d", "--build")
Write-Host ($ComposeUp.Output -join [Environment]::NewLine)
if ($ComposeUp.ExitCode -ne 0) {
    Write-Host "docker compose up fallo. Revisa la salida anterior y ejecuta docker compose logs." -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Esperando servicios..." -ForegroundColor Cyan
Wait-Url "Prolog Service" "http://localhost:8001/health"
Wait-Url "Telegram Service" "http://localhost:8002/health"
Wait-Url "API Gateway" "http://localhost:8000/api/health"
Wait-Url "Frontend" "http://localhost:$FrontendPort"

Write-Host ""
Write-Host ("todo est{0} subido en:" -f [char]0x00E1) -ForegroundColor Green
Write-Host "Frontend:          http://localhost:$FrontendPort" -ForegroundColor Green
Write-Host "API Gateway docs:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "API health:        http://localhost:8000/api/health" -ForegroundColor Green
Write-Host "Prolog health:     http://localhost:8001/health" -ForegroundColor Green
Write-Host "Telegram health:   http://localhost:8002/health" -ForegroundColor Green
Write-Host ""
Write-Host "Para detener Docker: .\scripts\stop_docker_windows.ps1" -ForegroundColor Cyan

Pop-Location
