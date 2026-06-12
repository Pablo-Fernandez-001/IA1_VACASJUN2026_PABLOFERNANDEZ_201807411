$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$EnvPath = Join-Path $ProjectRoot ".env"
$ApiPort = "8100"
if (Test-Path $EnvPath) {
    $Line = Get-Content $EnvPath | Where-Object { $_ -match "^API_PORT=" } | Select-Object -First 1
    if ($Line) { $ApiPort = ($Line -replace "^API_PORT=", "").Trim() }
}

$BaseUrl = "http://localhost:$ApiPort"
$body = @{ username = "IA1-User"; password = "IA1-password@_new" } | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/auth/login" -ContentType "application/json" -Body $body
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod -Uri "$BaseUrl/api/stats" -Headers $headers
