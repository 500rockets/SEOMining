# Wait for services to be ready
Write-Host "Waiting for SEO Mining services to be ready..." -ForegroundColor Yellow
Write-Host ""

$maxAttempts = 60
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "[$attempt/$maxAttempts] Checking..." -NoNewline
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2
        
        if ($response.status -eq "healthy") {
            Write-Host " OK!" -ForegroundColor Green
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  SERVICES READY!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Status:" -ForegroundColor Cyan
            Write-Host "  API: http://localhost:8000" -ForegroundColor White
            Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor White
            
            if ($response.gpu_available) {
                Write-Host "  GPU: $($response.gpu_count) devices available" -ForegroundColor Green
            }
            
            Write-Host ""
            Write-Host "Run the test:" -ForegroundColor Cyan
            Write-Host "  .\test-500rockets-simple.ps1" -ForegroundColor White
            Write-Host ""
            exit 0
        }
    } catch {
        Write-Host " waiting..." -ForegroundColor Gray
    }
    
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "Timeout waiting for services. Check logs:" -ForegroundColor Red
Write-Host "  cd backend; docker-compose logs backend" -ForegroundColor Yellow
Write-Host ""
exit 1

