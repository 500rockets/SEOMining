#!/usr/bin/env pwsh
# Organized GPU Analysis Runner
# Runs analysis with proper output structure

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host " ORGANIZED GPU SEMANTIC ANALYSIS " -ForegroundColor Yellow -NoNewline
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Green
$dockerStatus = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if backend service is running
Write-Host "Checking backend service..." -ForegroundColor Green
$backendStatus = docker ps --filter "name=seo-mining-backend" --format "table {{.Names}}\t{{.Status}}"
if ($backendStatus -notmatch "Up") {
    Write-Host "❌ Backend service is not running. Starting services..." -ForegroundColor Red
    docker-compose up -d
    Start-Sleep -Seconds 10
}

Write-Host "✅ Services are running"
Write-Host ""

# Run organized analysis
Write-Host "🚀 Starting organized GPU analysis..." -ForegroundColor Green
Write-Host ""

docker exec seo-mining-backend python /app/app/organized_gpu_analysis.py

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host " ANALYSIS COMPLETE " -ForegroundColor Yellow -NoNewline
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

# Show output structure
Write-Host "📁 Output structure:" -ForegroundColor Green
docker exec seo-mining-backend find /app/output -type f -name "*.json" -o -name "*.md" | Sort-Object

Write-Host ""
Write-Host "📋 Quick access:" -ForegroundColor Yellow
Write-Host "  Latest analysis: docker exec seo-mining-backend ls -la /app/output/500rockets/latest/"
Write-Host "  View summary: docker exec seo-mining-backend cat /app/output/500rockets/latest/reports/summary_report_*.md"
Write-Host ""
