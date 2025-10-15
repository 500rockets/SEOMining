# SEO Mining Status Check Script
# Quick overview of system status

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SEO Mining Status Check             " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "[Docker]" -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running" -ForegroundColor Red
    Write-Host "   Start Docker Desktop and try again" -ForegroundColor White
    exit 1
}

# Check GPU
Write-Host "`n[GPU]" -ForegroundColor Yellow
try {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>$null
    if ($gpuInfo) {
        Write-Host "✅ NVIDIA GPU(s) detected:" -ForegroundColor Green
        $gpuInfo | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    }
} catch {
    Write-Host "⚠️  Could not detect GPU" -ForegroundColor Yellow
}

# Check services
Write-Host "`n[Services]" -ForegroundColor Yellow
cd D:\Sites\SEO_Mining\backend

$services = @("postgres", "redis", "backend", "celery-worker", "flower")
$runningCount = 0

foreach ($service in $services) {
    $status = docker-compose ps $service 2>$null | Select-String "running"
    if ($status) {
        Write-Host "✅ $service is running" -ForegroundColor Green
        $runningCount++
    } else {
        Write-Host "❌ $service is not running" -ForegroundColor Red
    }
}

if ($runningCount -eq 0) {
    Write-Host "`n⚠️  No services running. Start them with:" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   docker-compose up -d" -ForegroundColor White
}

# Check API
Write-Host "`n[API]" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2
    Write-Host "✅ API is responding" -ForegroundColor Green
    if ($response.gpu_available) {
        Write-Host "✅ GPU available in API: $($response.gpu_count) GPU(s)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  GPU not available in API" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ API is not responding" -ForegroundColor Red
}

# Check build progress
Write-Host "`n[Build Status]" -ForegroundColor Yellow
$images = docker images | Select-String "seo-mining-backend"
if ($images) {
    Write-Host "✅ Backend image built" -ForegroundColor Green
} else {
    Write-Host "⏳ Backend image still building or not built" -ForegroundColor Yellow
    Write-Host "   Check build logs with: docker-compose logs --follow" -ForegroundColor White
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Status check complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nUseful URLs:" -ForegroundColor Cyan
Write-Host "• API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "• API Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "• Flower: http://localhost:5555" -ForegroundColor White
Write-Host ""

