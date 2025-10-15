# SEO Mining - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SEO MINING ARCHITECTURE                                │
│                    GPU-Accelerated Local Processing                              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│  USER INTERFACE                                                               │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  API Client      │  │  Web UI          │  │  CLI Tool        │          │
│  │  (curl/Postman)  │  │  (Future)        │  │  (Future)        │          │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘          │
│           │                     │                     │                     │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────┘
            │                     │                     │
            └──────────────┬──────┴─────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  API LAYER (Port 8000)                                                        │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  FastAPI Application                                                    │ │
│  │                                                                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │ │
│  │  │ /analyze     │  │ /jobs/{id}   │  │ /optimize    │  │ /health    │ │ │
│  │  │ Start job    │  │ Check status │  │ Optimize page│  │ GPU status │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────┬───────┘ │ │
│  └─────────┼──────────────────┼──────────────────┼──────────────┼─────────┘ │
│            │                  │                  │              │           │
└────────────┼──────────────────┼──────────────────┼──────────────┼───────────┘
             │                  │                  │              │
             ▼                  ▼                  ▼              ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  JOB QUEUE (Celery + Redis)                                                   │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Redis (Port 6379)                                                      │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  Queue: analysis.tasks │ Queue: optimization.tasks  │ Results    │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Celery Workers (4 concurrent)                                          │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │ │
│  │  │ Worker 1   │  │ Worker 2   │  │ Worker 3   │  │ Worker 4   │       │ │
│  │  │ GPU 0      │  │ GPU 1      │  │ GPU 0      │  │ GPU 1      │       │ │
│  │  └────┬───────┘  └────┬───────┘  └────┬───────┘  └────┬───────┘       │ │
│  └───────┼──────────────┼──────────────┼──────────────┼────────────────────┘ │
└──────────┼──────────────┼──────────────┼──────────────┼────────────────────────┘
           │              │              │              │
           └──────────────┴──────────────┴──────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  BUSINESS LOGIC LAYER                                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Analysis Service (Phase 2)                                             │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │ │
│  │  │ Fetch SERP │→ │ Scrape     │→ │ Extract    │→ │ Generate   │       │ │
│  │  │ results    │  │ pages      │  │ text       │  │ embeddings │       │ │
│  │  └────────────┘  └────────────┘  └────────────┘  └──────┬─────┘       │ │
│  │                                                          │               │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────▼──────┐       │ │
│  │  │ Generate   │← │ Calculate  │← │ Cluster    │← │ Store      │       │ │
│  │  │ report     │  │ scores     │  │ topics     │  │ embeddings │       │ │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Optimization Service (Phase 3)                                         │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │ │
│  │  │ Hash page  │→ │ Generate   │→ │ Test       │→ │ Keep best  │       │ │
│  │  │ components │  │ variations │  │ with cache │  │ changes    │       │ │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  SERVICE LAYER                                                                │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  EMBEDDINGS (Phase 2)                                                │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  Local GPU Embedder                                            │  │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │  │   │
│  │  │  │ GPU 0    │  │ GPU 1    │  │ Model    │                     │  │   │
│  │  │  │ RTX 4000 │  │ RTX 4000 │  │ Cache    │                     │  │   │
│  │  │  │ Batch 128│  │ Batch 128│  │ mpnet    │                     │  │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘                     │  │   │
│  │  │  → 500 embeddings/second                                       │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  SCORING (Phase 2)                                                   │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ Alignment  │  │ Coverage   │  │ Metadata   │  │ Hierarchy  │    │   │
│  │  │ Scorer     │  │ Scorer     │  │ Scorer     │  │ Scorer     │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ Thematic   │  │ Balance    │  │ Query      │  │ Composite  │    │   │
│  │  │ Unity      │  │ Scorer     │  │ Intent     │  │ Scorer     │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  SCRAPING (Phase 2)                                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                     │   │
│  │  │ Page       │  │ Text       │  │ Proxy      │                     │   │
│  │  │ Fetcher    │  │ Extractor  │  │ Manager    │                     │   │
│  │  │            │  │ (HTML→txt) │  │ (50 prox.) │                     │   │
│  │  └────────────┘  └────────────┘  └────────────┘                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  ANALYSIS (Phase 2)                                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                     │   │
│  │  │ Clustering │  │ Analysis   │  │ Report     │                     │   │
│  │  │ Service    │  │ Service    │  │ Generator  │                     │   │
│  │  │ (HDBSCAN)  │  │            │  │            │                     │   │
│  │  └────────────┘  └────────────┘  └────────────┘                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  OPTIMIZATION (Phase 3)                                              │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ Page       │  │ Change     │  │ Dependency │  │ Cached     │    │   │
│  │  │ Hash       │  │ Set        │  │ Graph      │  │ Score Mgr  │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │   │
│  │  ┌────────────┐  ┌────────────┐                                     │   │
│  │  │ Incremen-  │  │ Hashing    │                                     │   │
│  │  │ tal Calc   │  │ Optimizer  │                                     │   │
│  │  └────────────┘  └────────────┘                                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                                   │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database (Port 5432)                                     │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                     │   │
│  │  │ analysis_  │  │ analysis_  │  │ alembic_   │                     │   │
│  │  │ jobs       │  │ results    │  │ version    │                     │   │
│  │  │            │  │ (8+ scores)│  │            │                     │   │
│  │  └────────────┘  └────────────┘  └────────────┘                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  File Storage                                                        │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ data/raw/  │  │ data/proc/ │  │ output/    │  │ config/    │    │   │
│  │  │ (HTML)     │  │ (embeddings│  │ (reports)  │  │ (proxies)  │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  EXTERNAL SERVICES                                                            │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  ValueSerp API                                                       │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  GET /search?q={keyword}                                       │  │   │
│  │  │  → Returns top 10 organic results                              │  │   │
│  │  │  → Cost: $0.005 per query                                      │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  50 Rotating Proxies (Optional)                                     │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  Proxy 1-50: HTTP/HTTPS proxies                               │  │   │
│  │  │  → Health monitoring                                           │  │   │
│  │  │  → Round-robin rotation                                        │  │   │
│  │  │  → No direct connections                                       │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Competitor Websites                                                 │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  Top 10 ranking pages                                          │  │   │
│  │  │  → Scraped via proxies                                         │  │   │
│  │  │  → HTML stored locally                                         │  │   │
│  │  │  → No direct connections                                       │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│  HARDWARE LAYER                                                               │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  2x NVIDIA Quadro RTX 4000                                           │   │
│  │  ┌────────────────────────────────┐  ┌────────────────────────────┐  │   │
│  │  │  GPU 0 (CUDA Device 0)         │  │  GPU 1 (CUDA Device 1)     │  │   │
│  │  │  ├─ 8GB VRAM                   │  │  ├─ 8GB VRAM               │  │   │
│  │  │  ├─ 2,304 CUDA cores           │  │  ├─ 2,304 CUDA cores       │  │   │
│  │  │  ├─ Batch size: 128            │  │  ├─ Batch size: 128        │  │   │
│  │  │  └─ ~250 embeddings/sec        │  │  └─ ~250 embeddings/sec    │  │   │
│  │  └────────────────────────────────┘  └────────────────────────────┘  │   │
│  │  Total Throughput: ~500 embeddings/second                           │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Docker Desktop + NVIDIA Container Toolkit                           │   │
│  │  ├─ WSL2 backend                                                     │   │
│  │  ├─ NVIDIA runtime                                                   │   │
│  │  ├─ GPU passthrough enabled                                          │   │
│  │  └─ CUDA 12.1 support                                                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Analysis Workflow (Phase 2)

```
1. User Request
   ↓
2. POST /api/v1/analyze
   {"url": "example.com", "keyword": "prescription glasses"}
   ↓
3. Create Job in Database
   job_id = "abc-123"
   ↓
4. Queue Celery Task
   analysis_task.apply_async(job_id)
   ↓
5. Celery Worker Picks Up Task
   ↓
6. Fetch SERP Results (ValueSerp API)
   → Get top 10 competitor URLs
   ↓
7. Scrape Competitor Pages (via proxies)
   → Download HTML
   → Store in data/raw/
   ↓
8. Extract Text from All Pages (your page + 10 competitors)
   → Title, meta, H1-H6, sections
   → Clean content
   ↓
9. Generate Embeddings (GPU)
   ┌─────────────────────────────┐
   │ GPU 0: Batch 1-128          │
   │ GPU 1: Batch 129-256        │
   └─────────────────────────────┘
   → Your page embedding
   → 10 competitor page embeddings
   → Section embeddings (~80 vectors)
   ↓
10. Cluster Competitor Topics (HDBSCAN)
    → Group similar sections
    → Identify 5-10 topic clusters
    ↓
11. Calculate All Scores
    ├─ Alignment (semantic similarity)
    ├─ Coverage (topic cluster coverage)
    ├─ Metadata (title/meta/H1 alignment)
    ├─ Hierarchy (H1→H2→H3 logic)
    ├─ Thematic Unity (consistency)
    ├─ Balance (section lengths)
    ├─ Query Intent (query type match)
    └─ Composite (weighted average)
    ↓
12. Store Results in Database
    analysis_results table (8+ scores)
    ↓
13. Generate Report
    JSON/HTML with scores, recommendations
    ↓
14. Update Job Status
    status = "completed"
    ↓
15. User Retrieves Results
    GET /api/v1/jobs/abc-123/results
    ← Returns full analysis
```

### Optimization Workflow (Phase 3)

```
1. User Request
   ↓
2. POST /api/v1/optimize
   {"url": "example.com", "keyword": "prescription glasses", "max_iterations": 100}
   ↓
3. Run Initial Analysis
   → Get baseline scores
   ↓
4. Hash Page Components (NANO→MICRO→MESO→MACRO→MEGA)
   ├─ NANO: Individual words
   ├─ MICRO: Sentences
   ├─ MESO: Sections
   ├─ MACRO: Sections groups
   └─ MEGA: Full page
   ↓
5. Build Dependency Graph
   → Map hash levels to affected scores
   ↓
6. Optimization Loop (iterate 100x):
   ├─ Generate word-level variation
   │  → Add/remove/replace words
   ├─ Detect changed hash levels
   │  → Only NANO and MICRO changed
   ├─ Determine affected scores
   │  → Only metadata + alignment need recalc
   ├─ Retrieve cached scores (93%+ hit rate)
   │  → Coverage, hierarchy, thematic unity, balance, query intent (unchanged)
   ├─ Recalculate affected scores (7%)
   │  → Metadata + alignment (from cache)
   ├─ Compare to baseline
   │  → New composite score vs old
   ├─ Keep if improved
   │  └─ Update baseline, cache new scores
   └─ Discard if worse
   ↓
7. Return Optimized Version
   ← Best version after 100 iterations
   ← Score improvements by dimension
   ← Specific changes made
```

## Technology Stack

### Backend
- **API**: FastAPI (async, OpenAPI docs)
- **Queue**: Celery (distributed task queue)
- **Broker**: Redis (message broker, caching)
- **Database**: PostgreSQL (job/result persistence)
- **Migrations**: Alembic (schema management)

### ML/AI
- **Embeddings**: sentence-transformers (local GPU)
- **Model**: all-mpnet-base-v2 (420M params)
- **Clustering**: HDBSCAN (density-based)
- **Similarity**: cosine similarity (numpy/scipy)
- **GPU**: PyTorch + CUDA 12.1

### Infrastructure
- **Container**: Docker + docker-compose
- **GPU Support**: NVIDIA Container Toolkit
- **Runtime**: NVIDIA runtime
- **OS**: Windows 10/11 with WSL2

### External
- **SERP API**: ValueSerp ($0.005/query)
- **Proxies**: 50 rotating proxies (optional)

## Ports & Services

| Service | Port | Purpose |
|---------|------|---------|
| backend | 8000 | FastAPI REST API |
| flower | 5555 | Celery monitoring |
| postgres | 5432 | Database |
| redis | 6379 | Queue + cache |

## Data Storage

```
backend/
├── data/
│   ├── raw/          # Scraped HTML pages
│   ├── processed/    # Embeddings, analysis
│   └── cache/        # Temporary data
├── output/
│   ├── bulk/         # Bulk analysis results
│   └── reports/      # Generated reports
└── config/
    └── proxies.txt   # 50 proxy addresses
```

## Performance Characteristics

### Speed
- Embeddings: ~500/second (dual GPU)
- Analysis: <30 seconds per page
- Optimization: <5 minutes (100 iterations)

### Efficiency
- Cache hit rate: 93%+ (optimization)
- GPU utilization: >80%
- Concurrent workers: 4

### Cost
- SERP API: $0.005 per keyword
- Embeddings: $0.000 (local GPU)
- Scraping: $0.000 (local + proxies)
- **Total: $0.005 per keyword** (vs $0.075 cloud)

---

See `WINDOWS_GPU_SETUP.md` for setup instructions  
See `PROGRESS.md` for development roadmap  
See `QUICK_REFERENCE.md` for daily commands


