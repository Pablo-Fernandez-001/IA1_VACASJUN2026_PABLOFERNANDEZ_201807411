param(
    [switch]$SaveFirst
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

function Set-EnvValue {
    param(
        [string]$Name,
        [string]$Value
    )
    $Lines = Get-Content $EnvPath
    $Found = $false
    $Updated = $Lines | ForEach-Object {
        if ($_ -match "^$Name=") {
            $Found = $true
            "$Name=$Value"
        }
        else {
            $_
        }
    }
    if (-not $Found) {
        $Updated += "$Name=$Value"
    }
    Set-Content -LiteralPath $EnvPath -Value $Updated -Encoding UTF8
}

$Token = Get-EnvValue "TELEGRAM_BOT_TOKEN"
if (-not $Token) {
    throw "TELEGRAM_BOT_TOKEN esta vacio en .env."
}

$Bot = Invoke-RestMethod "https://api.telegram.org/bot$Token/getMe"
Write-Host "Bot configurado: @$($Bot.result.username)" -ForegroundColor Green

$Updates = Invoke-RestMethod "https://api.telegram.org/bot$Token/getUpdates"
if (-not $Updates.result -or $Updates.result.Count -eq 0) {
    Write-Host "Telegram todavia no devolvio ningun chat_id." -ForegroundColor Yellow
    Write-Host "Abre este enlace, presiona Start o envia /start:" -ForegroundColor Yellow
    Write-Host "https://t.me/$($Bot.result.username)" -ForegroundColor Cyan
    Write-Host "Luego vuelve a ejecutar:" -ForegroundColor Yellow
    Write-Host ".\scripts\telegram_chat_id_windows.ps1 -SaveFirst" -ForegroundColor Cyan
    exit 0
}

$Chats = @{}
foreach ($Update in $Updates.result) {
    $Message = $Update.message
    if (-not $Message) { $Message = $Update.edited_message }
    if (-not $Message) { continue }

    $Chat = $Message.chat
    $NameParts = @($Chat.first_name, $Chat.last_name, $Chat.title) | Where-Object { $_ }
    $DisplayName = ($NameParts -join " ").Trim()
    if (-not $DisplayName) { $DisplayName = $Chat.username }
    if (-not $DisplayName) { $DisplayName = "(sin nombre)" }

    $Chats["$($Chat.id)"] = [pscustomobject]@{
        chat_id = "$($Chat.id)"
        type = $Chat.type
        name = $DisplayName
    }
}

$ChatList = $Chats.Values | Sort-Object type, name
$ChatList | Format-Table -AutoSize

if ($SaveFirst -and $ChatList.Count -gt 0) {
    $Preferred = $ChatList | Where-Object { $_.type -eq "private" } | Select-Object -First 1
    if (-not $Preferred) { $Preferred = $ChatList | Select-Object -First 1 }
    Set-EnvValue "TELEGRAM_DEFAULT_CHAT_ID" $Preferred.chat_id
    Write-Host "TELEGRAM_DEFAULT_CHAT_ID guardado en .env: $($Preferred.chat_id)" -ForegroundColor Green
    Write-Host "Reinicia servicios para que tomen el nuevo valor." -ForegroundColor Cyan
}
