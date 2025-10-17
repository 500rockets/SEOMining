# Simple script to copy SEO analysis results from Docker container
Write-Host "Copying SEO analysis results..." -ForegroundColor Green

# Check if container is running
$containerName = "seo-mining-backend"
$containerRunning = docker ps --filter "name=$containerName" --format "{{.Names}}"

if (-not $containerRunning) {
    Write-Host "❌ Container '$containerName' is not running." -ForegroundColor Red
    Write-Host "Run: docker-compose -f backend/docker-compose.yml up -d" -ForegroundColor Yellow
    exit 1
}

# Create output directory
if (-not (Test-Path "./output")) {
    New-Item -ItemType Directory -Path "./output" -Force | Out-Null
}

# Copy from new structure first
Write-Host "📂 Copying from new structure..." -ForegroundColor Cyan
docker cp "$containerName`:/app/output/projects/500rockets" "./output/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully copied project data!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Key files:" -ForegroundColor Cyan
    Write-Host "   📊 Executive Summary: ./output/500rockets/07_final_reports/executive_summary/executive_summary.md" -ForegroundColor White
    Write-Host "   💡 Recommendations: ./output/500rockets/06_optimization/recommendations.json" -ForegroundColor White
    Write-Host "   🔍 Semantic Gaps: ./output/500rockets/06_optimization/semantic_gaps.json" -ForegroundColor White
} else {
    Write-Host "❌ Failed to copy project data" -ForegroundColor Red
}