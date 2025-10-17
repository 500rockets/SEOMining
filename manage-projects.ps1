#!/usr/bin/env pwsh
# Hierarchical Project Manager
# Manages company projects with multiple URL/Keyword sub-projects

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host " HIERARCHICAL SEO PROJECT MANAGER " -ForegroundColor Yellow -NoNewline
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

# Show current project structure
Write-Host "📁 Current Project Structure:" -ForegroundColor Green
docker exec seo-mining-backend find /app/projects -type d -maxdepth 2 | Sort-Object

Write-Host ""
Write-Host "🏢 To manage projects, run:" -ForegroundColor Yellow
Write-Host "   docker exec -it seo-mining-backend python /app/app/hierarchical_project_manager.py"
Write-Host ""

# Ask if user wants to manage projects now
$manage = Read-Host "Do you want to manage projects now? (y/n)"
if ($manage -eq "y" -or $manage -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Starting project manager..." -ForegroundColor Green
    docker exec -it seo-mining-backend python /app/app/hierarchical_project_manager.py
} else {
    Write-Host ""
    Write-Host "📋 Project Structure:" -ForegroundColor Cyan
    Write-Host "   Company Projects: /app/projects/{company_name}/"
    Write-Host "   Sub-Projects: /app/projects/{company_name}/sub_projects/{url_slug}_{keyword_slug}/"
    Write-Host ""
    Write-Host "📝 Example Structure:" -ForegroundColor Cyan
    Write-Host "   /app/projects/500rockets/"
    Write-Host "   ├── company_config.json"
    Write-Host "   ├── sub_projects/"
    Write-Host "   │   ├── homepage_marketing-agency-services/"
    Write-Host "   │   ├── services_digital-marketing/"
    Write-Host "   │   └── blog_seo-tips/"
    Write-Host "   └── reports/"
    Write-Host ""
    Write-Host "🚀 Ready to create and manage projects!"
}
