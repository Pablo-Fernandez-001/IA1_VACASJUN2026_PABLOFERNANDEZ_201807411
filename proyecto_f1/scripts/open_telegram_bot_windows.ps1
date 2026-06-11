$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$EnvPath = Join-Path $ProjectRoot ".env"

if (-not (Test-Path $EnvPath)) {
    throw "No existe .env. Ejecuta primero .\scripts\setup_windows.ps1."
}

$Token = (Get-Content $EnvPath | Where-Object { $_ -match "^TELEGRAM_BOT_TOKEN=" } | Select-Object -First 1) -replace "^TELEGRAM_BOT_TOKEN=", ""
if (-not $Token) {
    throw "TELEGRAM_BOT_TOKEN esta vacio en .env."
}

$Bot = Invoke-RestMethod "https://api.telegram.org/bot$Token/getMe"
$Url = "https://t.me/$($Bot.result.username)"

Write-Host "Abriendo $Url" -ForegroundColor Cyan
Write-Host "En Telegram presiona Start o envia /start. Luego ejecuta:" -ForegroundColor Yellow
Write-Host ".\scripts\telegram_chat_id_windows.ps1 -SaveFirst" -ForegroundColor Cyan
Start-Process $Url
