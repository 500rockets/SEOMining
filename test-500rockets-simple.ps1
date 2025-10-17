# Simple test of 500rockets.io content scoring

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  500 ROCKETS.IO - CONTENT SCORING" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$API_BASE = "http://localhost:8000/api/v1"

# Check status first
Write-Host "[1/3] Checking API status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "OK API is healthy" -ForegroundColor Green
    if ($health.gpu_available) {
        Write-Host "OK GPU available: $($health.gpu_count) devices" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR API not responding" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] Testing embeddings service..." -ForegroundColor Yellow
$embeddingTest = @{
    text = "500 Rockets digital marketing agency"
} | ConvertTo-Json

try {
    $embResult = Invoke-RestMethod -Uri "$API_BASE/embeddings/embed" -Method Post -Body $embeddingTest -ContentType "application/json"
    Write-Host "OK Generated embedding with dimension: $($embResult.dimension)" -ForegroundColor Green
} catch {
    Write-Host "ERROR Embeddings failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "[3/3] Scoring 500rockets content..." -ForegroundColor Yellow

# Simple content object
$content = @{
    text = "500 Rockets is a digital marketing agency. We help businesses grow through SEO and content marketing. Our team delivers data-driven marketing strategies. We work with startups and established companies to achieve measurable results."
    title = "500 Rockets - Digital Marketing Agency"
    description = "Digital marketing agency specializing in SEO and growth"
    query = "marketing agency services"
}

$json = $content | ConvertTo-Json

try {
    $score = Invoke-RestMethod -Uri "$API_BASE/scoring/score" -Method Post -Body $json -ContentType "application/json"
    
    Write-Host "OK Content scored successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  500ROCKETS.IO SCORES:" -ForegroundColor Cyan
    Write-Host "  ----------------------------------------"
    Write-Host "  Metadata Alignment:         $([math]::Round($score.metadata_alignment, 1))/100"
    Write-Host "  Hierarchical Decomposition: $([math]::Round($score.hierarchical_decomposition, 1))/100"
    Write-Host "  Thematic Unity:             $([math]::Round($score.thematic_unity, 1))/100"
    Write-Host "  Balance:                    $([math]::Round($score.balance, 1))/100"
    Write-Host "  Query Intent:               $([math]::Round($score.query_intent, 1))/100"
    Write-Host "  Structural Coherence:       $([math]::Round($score.structural_coherence, 1))/100"
    Write-Host "  ----------------------------------------"
    Write-Host "  Composite Score:            $([math]::Round($score.composite_score, 1))/100" -ForegroundColor Yellow
    Write-Host "  SEO Score:                  $([math]::Round($score.seo_score, 1))/100" -ForegroundColor Green
    Write-Host "  ----------------------------------------"
    Write-Host ""
    Write-Host "  Top Recommendations:" -ForegroundColor Cyan
    $i = 1
    foreach ($rec in $score.recommendations | Select-Object -First 3) {
        Write-Host "  $i. $rec" -ForegroundColor Gray
        $i++
    }
    
} catch {
    Write-Host "ERROR Scoring failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTING COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

