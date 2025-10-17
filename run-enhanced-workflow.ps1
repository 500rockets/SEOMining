#!/usr/bin/env pwsh
# Enhanced SEO Analysis Workflow Runner with Proxy Support
# Runs the entire process with proper proxy configuration

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host " ENHANCED SEO ANALYSIS WORKFLOW WITH PROXIES " -ForegroundColor Yellow -NoNewline
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

# Check proxy configuration
Write-Host "🔧 Checking proxy configuration..." -ForegroundColor Green
$proxyConfig = docker exec seo-mining-backend cat /app/.env | Select-String "USE_PROXIES|PROXY_FILE"
Write-Host $proxyConfig
Write-Host ""

# Show project structure
Write-Host "📁 Project structure:" -ForegroundColor Green
docker exec seo-mining-backend ls -la /app/projects/500rockets/

Write-Host ""
Write-Host "🚀 Starting enhanced workflow with proxy support..." -ForegroundColor Green
Write-Host ""

# Run the enhanced workflow
docker exec seo-mining-backend python /app/app/enhanced_workflow_runner.py

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host " ENHANCED WORKFLOW COMPLETE " -ForegroundColor Yellow -NoNewline
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

# Show final structure
Write-Host "📁 Final project structure:" -ForegroundColor Green
docker exec seo-mining-backend find /app/projects/500rockets -name "*.json" -o -name "*.md" | Sort-Object

Write-Host ""
Write-Host "📋 Quick access:" -ForegroundColor Yellow
Write-Host "  Executive Summary: docker exec seo-mining-backend cat /app/projects/500rockets/07_final_reports/executive_summary/executive_summary.md"
Write-Host "  Recommendations: docker exec seo-mining-backend cat /app/projects/500rockets/06_optimization/recommendations.json"
Write-Host "  Semantic Gaps: docker exec seo-mining-backend cat /app/projects/500rockets/06_optimization/semantic_gaps.json"
Write-Host "  Project Config: docker exec seo-mining-backend cat /app/projects/500rockets/00_config/project_config.json"
Write-Host ""

# Show proxy usage summary
Write-Host "🔧 Proxy Usage Summary:" -ForegroundColor Cyan
Write-Host "  - Competitor content scraped with proxy support"
Write-Host "  - All scraping attempts logged with proxy status"
Write-Host "  - Failed scrapes saved to failed_scrapes/ folder"
Write-Host ""
