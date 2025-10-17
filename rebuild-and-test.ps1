# Rebuild services and run full analysis
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REBUILDING WITH ASYNC PLAYWRIGHT FIX" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Waiting for rebuild to complete..." -ForegroundColor Yellow
Write-Host "(This may take 2-3 minutes)" -ForegroundColor Gray
Write-Host ""

# Wait a bit for build to start
Start-Sleep -Seconds 10

# Wait for services to be healthy
$maxWait = 180  # 3 minutes
$waited = 0
$healthy = $false

while ($waited -lt $maxWait -and -not $healthy) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($health.status -eq "healthy") {
            $healthy = $true
            Write-Host "OK Services are healthy!" -ForegroundColor Green
            break
        }
    } catch {
        # Still starting
    }
    
    Write-Host "." -NoNewline -ForegroundColor Gray
    Start-Sleep -Seconds 5
    $waited += 5
}

Write-Host ""
Write-Host ""

if (-not $healthy) {
    Write-Host "ERROR Services did not become healthy in time" -ForegroundColor Red
    Write-Host "Check logs: cd backend; docker-compose logs backend" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RUNNING 500ROCKETS.IO ANALYSIS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the full analysis
powershell -ExecutionPolicy Bypass -File .\run-full-analysis.ps1

