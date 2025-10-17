#!/usr/bin/env pwsh
# Enhanced Scraping Script
# Handles spam protection and creates manual content files automatically

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host " ENHANCED COMPETITOR SCRAPING " -ForegroundColor Yellow -NoNewline
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
$backendStatus = docker-compose ps backend 2>$null
if ($backendStatus -notmatch "Up") {
    Write-Host "❌ Backend service is not running. Starting services..." -ForegroundColor Red
    docker-compose up -d
    Start-Sleep -Seconds 10
}

# Run enhanced scraping
Write-Host "Starting enhanced scraping..." -ForegroundColor Green
Write-Host ""

docker-compose exec backend python /app/app/enhanced_scraping.py

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host " SCRAPING COMPLETE " -ForegroundColor Yellow -NoNewline
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

# Show created files
Write-Host "Created files:" -ForegroundColor Green
docker-compose exec backend ls -la /app/manual_content/

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review the created files in /app/manual_content/"
Write-Host "2. Run the GPU analysis: docker-compose exec backend python /app/app/working-gpu-analysis.py"
Write-Host ""

# Ask if user wants to run analysis
$runAnalysis = Read-Host "Run GPU analysis now? (y/n)"
if ($runAnalysis -eq "y" -or $runAnalysis -eq "Y") {
    Write-Host ""
    Write-Host "Running GPU analysis..." -ForegroundColor Green
    docker-compose exec backend python /app/app/working-gpu-analysis.py
}
