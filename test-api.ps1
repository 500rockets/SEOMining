# SEO Mining API Test Script
# Quick tests to verify API is working

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SEO Mining API Test Suite           " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$apiBase = "http://localhost:8000"

# Test 1: Health Check
Write-Host "[1/4] Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$apiBase/health" -Method Get
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   GPU Available: $($response.gpu_available)" -ForegroundColor White
    if ($response.gpu_count) {
        Write-Host "   GPU Count: $($response.gpu_count)" -ForegroundColor White
        Write-Host "   GPUs: $($response.gpu_devices -join ', ')" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Root Endpoint
Write-Host "[2/4] Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$apiBase/" -Method Get
    Write-Host "✅ Root endpoint working" -ForegroundColor Green
    Write-Host "   Name: $($response.name)" -ForegroundColor White
    Write-Host "   Version: $($response.version)" -ForegroundColor White
} catch {
    Write-Host "❌ Root endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: API Documentation
Write-Host "[3/4] Checking API documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$apiBase/docs" -Method Get
    Write-Host "✅ API docs accessible" -ForegroundColor Green
    Write-Host "   URL: $apiBase/docs" -ForegroundColor White
} catch {
    Write-Host "❌ API docs not accessible: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Analysis Endpoint (basic check)
Write-Host "[4/4] Testing analysis endpoint..." -ForegroundColor Yellow
try {
    $body = @{
        url = "https://example.com"
        keyword = "test keyword"
        optimize = $false
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$apiBase/api/v1/analyze" `
        -Method Post `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "✅ Analysis endpoint working" -ForegroundColor Green
    Write-Host "   Job ID: $($response.job_id)" -ForegroundColor White
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    
    # Try to check job status
    Start-Sleep -Seconds 2
    Write-Host "   Checking job status..." -ForegroundColor White
    $jobStatus = Invoke-RestMethod -Uri "$apiBase/api/v1/jobs/$($response.job_id)" -Method Get
    Write-Host "   Job Status: $($jobStatus.status)" -ForegroundColor White
    
} catch {
    Write-Host "❌ Analysis endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Test Suite Complete                 " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. View API docs: $apiBase/docs" -ForegroundColor White
Write-Host "2. View Celery monitoring: http://localhost:5555" -ForegroundColor White
Write-Host "3. Check logs: cd backend && docker-compose logs -f" -ForegroundColor White
Write-Host ""

