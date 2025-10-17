#!/usr/bin/env pwsh
# Project Configuration Script
# Allows easy configuration of primary webpage and keyword

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host " SEO MINING PROJECT CONFIGURATION " -ForegroundColor Yellow -NoNewline
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

# Show current configuration
Write-Host "📋 Current Configuration:" -ForegroundColor Green
docker exec seo-mining-backend cat /app/projects/500rockets/00_config/project_config.json | ConvertFrom-Json | Format-List project_name, target_url, query, status

Write-Host ""
Write-Host "🔧 To update configuration, run:" -ForegroundColor Yellow
Write-Host "   docker exec -it seo-mining-backend python /app/app/config_manager.py"
Write-Host ""

# Ask if user wants to configure now
$configure = Read-Host "Do you want to configure the project now? (y/n)"
if ($configure -eq "y" -or $configure -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Starting configuration..." -ForegroundColor Green
    docker exec -it seo-mining-backend python /app/app/config_manager.py
} else {
    Write-Host ""
    Write-Host "📋 Current settings will be used:" -ForegroundColor Cyan
    Write-Host "   Target URL: https://500rockets.io"
    Write-Host "   Search Query: marketing agency services"
    Write-Host ""
    Write-Host "🚀 Ready to run analysis with current configuration!"
}
