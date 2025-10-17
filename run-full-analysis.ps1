# Full competitive analysis for 500rockets.io
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  500 ROCKETS.IO - FULL COMPETITIVE ANALYSIS" -ForegroundColor Green
Write-Host "  SERP → Scrape → Embed → Score → Insights" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$API_BASE = "http://localhost:8000/api/v1"

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Target URL: https://500rockets.io" -ForegroundColor White
Write-Host "  Query: 'marketing agency services'" -ForegroundColor White
Write-Host "  Top Competitors: 10" -ForegroundColor White
Write-Host "  Location: United States" -ForegroundColor White
Write-Host "  Proxy Rotation: Enabled" -ForegroundColor White
Write-Host ""

Write-Host "Starting analysis..." -ForegroundColor Yellow
Write-Host "This will take 1-3 minutes..." -ForegroundColor Gray
Write-Host ""

# Prepare request
$body = @{
    query = "marketing agency services"
    target_url = "https://500rockets.io"
    analyze_top_n = 10
    location = "United States"
    use_proxies = $true
} | ConvertTo-Json

try {
    Write-Host "[1/7] Fetching SERP results..." -ForegroundColor Yellow
    
    # Make the API call
    $result = Invoke-RestMethod -Uri "$API_BASE/full-analysis/analyze" `
        -Method Post `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 300
    
    Write-Host "OK Analysis complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  RESULTS" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Display target scores
    if ($result.target_score) {
        Write-Host "YOUR SCORES (500rockets.io):" -ForegroundColor Cyan
        Write-Host "  --------------------------------------------------------"
        Write-Host "  Metadata Alignment:         $([math]::Round($result.target_score.metadata_alignment, 1))/100"
        Write-Host "  Hierarchical Decomposition: $([math]::Round($result.target_score.hierarchical_decomposition, 1))/100"
        Write-Host "  Thematic Unity:             $([math]::Round($result.target_score.thematic_unity, 1))/100"
        Write-Host "  Balance:                    $([math]::Round($result.target_score.balance, 1))/100"
        Write-Host "  Query Intent:               $([math]::Round($result.target_score.query_intent, 1))/100"
        Write-Host "  Structural Coherence:       $([math]::Round($result.target_score.structural_coherence, 1))/100"
        Write-Host "  --------------------------------------------------------"
        Write-Host "  Composite Score:            $([math]::Round($result.target_score.composite_score, 1))/100" -ForegroundColor Yellow
        Write-Host "  SEO Score:                  $([math]::Round($result.target_score.seo_score, 1))/100" -ForegroundColor Green
        Write-Host "  --------------------------------------------------------"
        Write-Host ""
    }
    
    # Display competitor comparison
    Write-Host "TOP COMPETITORS:" -ForegroundColor Cyan
    Write-Host "  --------------------------------------------------------"
    $i = 1
    foreach ($comp in $result.competitors | Select-Object -First 5) {
        $urlShort = $comp.url -replace 'https?://', '' -replace 'www\.', ''
        if ($urlShort.Length -gt 40) { $urlShort = $urlShort.Substring(0, 40) + "..." }
        Write-Host "  $i. $urlShort" -ForegroundColor White
        Write-Host "     SEO Score: $([math]::Round($comp.seo_score, 1))/100 | Composite: $([math]::Round($comp.composite_score, 1))/100" -ForegroundColor Gray
        $i++
    }
    if ($result.competitors.Count -gt 5) {
        Write-Host "  ... and $($result.competitors.Count - 5) more competitors" -ForegroundColor Gray
    }
    Write-Host "  --------------------------------------------------------"
    Write-Host ""
    
    # Display insights
    if ($result.insights) {
        Write-Host "COMPETITIVE INSIGHTS:" -ForegroundColor Cyan
        Write-Host "  --------------------------------------------------------"
        
        if ($result.insights.average_competitor_score) {
            Write-Host "  Average Competitor Score: $([math]::Round($result.insights.average_competitor_score, 1))/100" -ForegroundColor White
        }
        
        if ($result.insights.target_vs_average) {
            $diff = $result.insights.target_vs_average.composite_score_diff
            $position = $result.insights.target_vs_average.position
            $color = if ($diff -gt 0) { "Green" } else { "Red" }
            Write-Host "  Your Position: $position ($([math]::Round($diff, 1)) points)" -ForegroundColor $color
        }
        
        Write-Host "  --------------------------------------------------------"
        Write-Host ""
    }
    
    # Display recommendations
    Write-Host "TOP RECOMMENDATIONS:" -ForegroundColor Cyan
    Write-Host "  --------------------------------------------------------"
    $recNum = 1
    foreach ($rec in $result.recommendations | Select-Object -First 5) {
        Write-Host "  $recNum. $rec" -ForegroundColor White
        $recNum++
    }
    Write-Host "  --------------------------------------------------------"
    Write-Host ""
    
    # Save full results to file
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $outputFile = "500rockets_analysis_$timestamp.json"
    $result | ConvertTo-Json -Depth 10 | Out-File $outputFile
    Write-Host "Full results saved to: $outputFile" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  ANALYSIS COMPLETE!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Analysis failed" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host ""
        Write-Host "API Response:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check if SERP API key is set in backend/.env" -ForegroundColor Gray
    Write-Host "  2. Verify services are running: docker-compose ps" -ForegroundColor Gray
    Write-Host "  3. Check logs: docker-compose logs backend" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

