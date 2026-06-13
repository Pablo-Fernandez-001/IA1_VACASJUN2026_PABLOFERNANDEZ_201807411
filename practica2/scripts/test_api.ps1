$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$EnvPath = Join-Path $ProjectRoot ".env"
$ApiPort = "8100"
if (Test-Path $EnvPath) {
    $Line = Get-Content $EnvPath | Where-Object { $_ -match "^API_PORT=" } | Select-Object -First 1
    if ($Line) { $ApiPort = ($Line -replace "^API_PORT=", "").Trim() }
}

$BaseUrl = "http://localhost:$ApiPort"
$loginBody = @{ username = "IA1-User"; password = "IA1-password@_new" } | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/auth/login" -ContentType "application/json" -Body $loginBody
$headers = @{ Authorization = "Bearer $($login.access_token)" }
$categories = Invoke-RestMethod -Uri "$BaseUrl/api/categories"
$questions = Invoke-RestMethod -Uri "$BaseUrl/api/questions"
$answers = Invoke-RestMethod -Uri "$BaseUrl/api/answers"
$search = Invoke-RestMethod -Uri "$BaseUrl/api/search?q=como%20levanto%20el%20proyecto&telegram_user=script"
$stats = Invoke-RestMethod -Uri "$BaseUrl/api/stats" -Headers $headers

[pscustomobject]@{
    health = (Invoke-RestMethod -Uri "$BaseUrl/api/health").status
    login = [bool]$login.access_token
    categories = $categories.Count
    questions = $questions.Count
    answers = $answers.Count
    search_found = $search.found
    logged_queries = $stats.total_queries
} | Format-List
