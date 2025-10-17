# Test 500rockets.io via API
# Real-world competitive analysis

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 68) -ForegroundColor Cyan
Write-Host "  🚀 500ROCKETS.IO - COMPETITIVE SEO ANALYSIS" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 68) -ForegroundColor Cyan
Write-Host ""

$API_BASE = "http://localhost:8000/api/v1"

# Test 1: Check pipeline status
Write-Host "[1/4] Checking pipeline status..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "$API_BASE/full-analysis/status" -Method Get
    Write-Host "✓ Pipeline operational" -ForegroundColor Green
    Write-Host "  - Embeddings: $($status.services.embeddings.status)" -ForegroundColor Gray
    Write-Host "  - Scraping: $($status.services.scraping.status)" -ForegroundColor Gray
    Write-Host "  - Scoring: $($status.services.scoring.status)" -ForegroundColor Gray
    Write-Host "  - SERP: $($status.services.serp.status)" -ForegroundColor Gray
    
    if ($status.services.embeddings.gpu_count) {
        Write-Host "  - GPU Count: $($status.services.embeddings.gpu_count)" -ForegroundColor Gray
    }
    if ($status.services.scraping.proxy_count) {
        Write-Host "  - Proxies: $($status.services.scraping.proxy_count)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Status check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Score 500rockets.io homepage content
Write-Host "[2/4] Scoring sample content..." -ForegroundColor Yellow

$sampleContent = @{
    text = @"
500 Rockets is a full-service digital marketing agency specializing in growth marketing, 
SEO optimization, and content strategy. We help businesses scale through data-driven marketing 
strategies and innovative digital solutions.

Our services include search engine optimization, content marketing, paid advertising, 
social media management, and conversion rate optimization. We work with startups and 
established businesses to achieve measurable growth.

With expertise in SEO, PPC, content creation, and analytics, we deliver results that matter. 
Our team combines technical excellence with creative strategy to drive sustainable growth 
for our clients.
"@
    title = "500 Rockets - Digital Marketing Agency"
    description = "Full-service digital marketing agency specializing in SEO, content marketing, and growth strategies"
    query = "marketing agency services"
}

try {
    $scoreResponse = Invoke-RestMethod -Uri "$API_BASE/scoring/score" -Method Post -Body ($sampleContent | ConvertTo-Json) -ContentType "application/json"
    
    Write-Host "✓ Content scored successfully" -ForegroundColor Green
    Write-Host ""
    Write-Host "  📊 500ROCKETS.IO CONTENT SCORES:" -ForegroundColor Cyan
    Write-Host "  " -NoNewline
    Write-Host ("━" * 50) -ForegroundColor DarkGray
    Write-Host "  1. Metadata Alignment:         $([math]::Round($scoreResponse.metadata_alignment, 1))/100" -ForegroundColor White
    Write-Host "  2. Hierarchical Decomposition: $([math]::Round($scoreResponse.hierarchical_decomposition, 1))/100" -ForegroundColor White
    Write-Host "  3. Thematic Unity:             $([math]::Round($scoreResponse.thematic_unity, 1))/100" -ForegroundColor White
    Write-Host "  4. Balance:                    $([math]::Round($scoreResponse.balance, 1))/100" -ForegroundColor White
    Write-Host "  5. Query Intent:               $([math]::Round($scoreResponse.query_intent, 1))/100" -ForegroundColor White
    Write-Host "  6. Structural Coherence:       $([math]::Round($scoreResponse.structural_coherence, 1))/100" -ForegroundColor White
    Write-Host "  " -NoNewline
    Write-Host ("━" * 50) -ForegroundColor DarkGray
    Write-Host "  7. Composite Score:            $([math]::Round($scoreResponse.composite_score, 1))/100" -ForegroundColor Yellow
    Write-Host "  8. SEO Score:                  $([math]::Round($scoreResponse.seo_score, 1))/100" -ForegroundColor Green
    Write-Host "  " -NoNewline
    Write-Host ("━" * 50) -ForegroundColor DarkGray
    
    Write-Host ""
    Write-Host "  ✅ TOP RECOMMENDATIONS:" -ForegroundColor Cyan
    $scoreResponse.recommendations | Select-Object -First 5 | ForEach-Object {
        Write-Host "    • $_" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "✗ Scoring failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Get scoring dimensions info
Write-Host "[3/4] Getting dimension information..." -ForegroundColor Yellow
try {
    $dimensions = Invoke-RestMethod -Uri "$API_BASE/scoring/dimensions" -Method Get
    Write-Host "✓ Retrieved $($dimensions.dimensions.Count) scoring dimensions" -ForegroundColor Green
    Write-Host "  All dimensions use 0-100 scale" -ForegroundColor Gray
} catch {
    Write-Host "✗ Failed to get dimensions: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: Show example full analysis request
Write-Host "[4/4] Full analysis example..." -ForegroundColor Yellow
Write-Host "✓ To run complete competitive analysis:" -ForegroundColor Green
Write-Host ""
Write-Host "  curl -X POST ""$API_BASE/full-analysis/analyze"" \" -ForegroundColor Cyan
Write-Host "    -H ""Content-Type: application/json"" \" -ForegroundColor Cyan
Write-Host "    -d '{" -ForegroundColor Cyan
Write-Host "      ""query"": ""marketing agency services""," -ForegroundColor Cyan
Write-Host "      ""target_url"": ""https://500rockets.io""," -ForegroundColor Cyan
Write-Host "      ""analyze_top_n"": 10" -ForegroundColor Cyan
Write-Host "    }'" -ForegroundColor Cyan
Write-Host ""
Write-Host "  This will:" -ForegroundColor Gray
Write-Host "    1. Fetch top 10 SERP results" -ForegroundColor Gray
Write-Host "    2. Scrape all competitor pages (with proxies)" -ForegroundColor Gray
Write-Host "    3. Generate embeddings on GPU" -ForegroundColor Gray
Write-Host "    4. Score across 8 dimensions" -ForegroundColor Gray
Write-Host "    5. Generate competitive insights" -ForegroundColor Gray
Write-Host "    6. Provide strategic recommendations" -ForegroundColor Gray
Write-Host ""
Write-Host "  ⏱️  Estimated time: 1-3 minutes for 10 competitors" -ForegroundColor Gray

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 68) -ForegroundColor Cyan
Write-Host "  ✅ TESTING COMPLETE!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 68) -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 View full API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

