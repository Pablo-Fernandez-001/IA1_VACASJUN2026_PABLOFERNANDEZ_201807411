param([switch]$SkipBuild)

$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $PSScriptRoot
Set-Location $project

docker compose config --quiet
if ($SkipBuild) { docker compose up -d } else { docker compose up --build -d }

$health = $null
for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8300/api/health" -TimeoutSec 3
        break
    } catch {
        Start-Sleep -Seconds 3
    }
}
if (-not $health) { throw "Backend no alcanzo estado saludable." }

$loginBody = @{ username = "admin"; password = "admin123" } | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8300/api/auth/login" -ContentType "application/json" -Body $loginBody
$token = $login.access_token
$headers = @{ Authorization = "Bearer $token" }

$invoicePath = Join-Path $project "data\facturas_generadas\factura_005.png"
$uploadJson = Join-Path $env:TEMP "smartinvoice_upload.json"
$httpCode = curl.exe -s -o $uploadJson -w "%{http_code}" -H "Authorization: Bearer $token" -F "file=@$invoicePath;type=image/png" "http://127.0.0.1:8300/api/invoices/upload"
if ($httpCode -ne "201") { throw "Carga fallo con HTTP $httpCode`: $(Get-Content -Raw $uploadJson)" }
$invoice = Get-Content -Raw $uploadJson | ConvertFrom-Json

$rpa = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8300/api/rpa/invoices/$($invoice.id)/register" -Headers $headers
$reportPath = Join-Path $project "reports\verificacion.csv"
Invoke-WebRequest -Uri "http://127.0.0.1:8300/api/reports/csv" -Headers $headers -OutFile $reportPath
$metrics = Invoke-RestMethod -Uri "http://127.0.0.1:8300/api/dashboard/metrics" -Headers $headers

$evidencePath = Join-Path $project "evidencias\docker\verificacion.txt"
$summary = @"
Fecha: $(Get-Date -Format o)
Health: $($health | ConvertTo-Json -Compress)
Factura: id=$($invoice.id), numero=$($invoice.invoice_number), estado=$($invoice.status)
RPA: id=$($rpa.id), estado=$($rpa.status), evidencia=$($rpa.evidence_path)
Metricas: $($metrics | ConvertTo-Json -Compress)
Reporte: $reportPath

$(docker compose ps)
"@
$summary | Set-Content -LiteralPath $evidencePath -Encoding UTF8
Write-Host "Verificacion completa. Evidencia: $evidencePath"
