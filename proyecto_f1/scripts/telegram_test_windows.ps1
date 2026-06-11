param(
    [string]$ChatId
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$EnvPath = Join-Path $ProjectRoot ".env"

if (-not (Test-Path $EnvPath)) {
    throw "No existe .env. Ejecuta primero .\scripts\setup_windows.ps1."
}

function Get-EnvValue {
    param([string]$Name)
    $Line = Get-Content $EnvPath | Where-Object { $_ -match "^$Name=" } | Select-Object -First 1
    if (-not $Line) { return "" }
    return ($Line -replace "^$Name=", "").Trim()
}

$Token = Get-EnvValue "TELEGRAM_BOT_TOKEN"
if (-not $Token) {
    throw "TELEGRAM_BOT_TOKEN esta vacio en .env."
}

if (-not $ChatId) {
    $ChatId = Get-EnvValue "TELEGRAM_DEFAULT_CHAT_ID"
}

if (-not $ChatId) {
    throw "No hay chat_id. Ejecuta .\scripts\telegram_chat_id_windows.ps1 -SaveFirst despues de enviar /start al bot."
}

$Payload = @{
    chat_id = $ChatId
    text = "Doctor Byte: prueba de Telegram lista."
} | ConvertTo-Json

$Response = Invoke-RestMethod "https://api.telegram.org/bot$Token/sendMessage" `
    -Method Post `
    -ContentType "application/json; charset=utf-8" `
    -Body $Payload

if ($Response.ok) {
    Write-Host "Mensaje enviado correctamente a Telegram." -ForegroundColor Green
}
else {
    $Response | ConvertTo-Json -Depth 5
}
