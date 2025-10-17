# Manual Content Management for Failed Scrapes
# Easy way to add competitor content when scraping fails

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan; Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "  MANUAL CONTENT MANAGEMENT" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan; Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""

Write-Host "When scraping fails, you can manually add competitor content for analysis." -ForegroundColor Yellow
Write-Host ""

Write-Host "Commands:" -ForegroundColor White
Write-Host "  Add Content:    docker-compose exec backend python /app/app/manual_content.py add" -ForegroundColor Gray
Write-Host "  List Content:   docker-compose exec backend python /app/app/manual_content.py list" -ForegroundColor Gray
Write-Host "  Preview:        docker-compose exec backend python /app/app/manual_content.py preview" -ForegroundColor Gray
Write-Host ""

Write-Host "Smart Analysis:   docker-compose exec backend python /app/app/smart-gpu-analysis.py" -ForegroundColor Green
Write-Host ""

Write-Host "=" -NoNewline -ForegroundColor Cyan; Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""

# Check if we have any manual content
Write-Host "Checking for existing manual content..." -ForegroundColor Yellow

$manualContent = docker-compose -f backend/docker-compose.yml exec backend python /app/app/manual_content.py list 2>$null

if ($manualContent -and $manualContent -notmatch "No manual content") {
    Write-Host "✓ Found existing manual content:" -ForegroundColor Green
    Write-Host $manualContent -ForegroundColor Gray
} else {
    Write-Host "No manual content found yet." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To add manual content:" -ForegroundColor White
    Write-Host "1. Copy the competitor page content from your browser" -ForegroundColor Gray
    Write-Host "2. Run: docker-compose exec backend python /app/app/manual_content.py add" -ForegroundColor Gray
    Write-Host "3. Paste the URL, title, and content when prompted" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Ready to run smart GPU analysis with manual content fallback!" -ForegroundColor Green
Write-Host ""

