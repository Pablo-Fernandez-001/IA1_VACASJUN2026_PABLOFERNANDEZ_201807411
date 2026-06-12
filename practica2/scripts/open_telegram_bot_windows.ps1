$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$EnvPath = Join-Path $ProjectRoot ".env"

if (-not (Test-Path $EnvPath)) {
    throw "No existe .env. Copia .env.example a .env y coloca el token del bot nuevo de SmartBot."
}

$Token = (Get-Content $EnvPath | Where-Object { $_ -match "^TELEGRAM_BOT_TOKEN=" } | Select-Object -First 1) -replace "^TELEGRAM_BOT_TOKEN=", ""
if (-not $Token) {
    throw "TELEGRAM_BOT_TOKEN esta vacio en .env. Crea un bot nuevo para Practica 2 con @BotFather."
}

$Bot = Invoke-RestMethod "https://api.telegram.org/bot$Token/getMe"
$Url = "https://t.me/$($Bot.result.username)"

Write-Host "Abriendo $Url" -ForegroundColor Cyan
Write-Host "Usa este chat para Practica 2, separado del bot del proyecto." -ForegroundColor Yellow
Write-Host "Luego ejecuta: .\scripts\telegram_chat_id_windows.ps1 -SaveFirst" -ForegroundColor Cyan
Start-Process $Url
