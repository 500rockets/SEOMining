# SEO Mining Architecture

## Overview
This project uses semantic analysis to compare your page against top-ranking search results, leveraging GPU acceleration for embedding generation and Docker for consistent deployment.

## System Components

### 1. Search Results Fetching (ValueSerp API)
**API Endpoint**: `https://api.valueserp.com/search`

**Configuration**:
- API Key: Stored in `.env` file (never committed)
- Location: 98146, Washington, United States
- Parameters: `gl=us`, `hl=en`, `google_domain=google.com`

**Process**:
1. Accept target keyword from user
2. Call ValueSerp API to get top 10 organic results
3. Extract URLs, titles, snippets, and positions
4. Store metadata in local database/JSON for tracking

### 2. Page Content Extraction
**Tools**:
- **Primary**: Custom spider/scraper (lightweight, controllable)
- **Optional**: SEO Screaming Frog integration for advanced crawling features

**Proxy Infrastructure**:
- **No Direct Connections**: All requests go through proxy pool
- **Proxy Pool Size**: 50 rotating proxies
- **Rotation Strategy**: 
  - Round-robin or random selection per request
  - Sticky sessions for multi-page crawls (same domain)
  - Automatic proxy cycling on failures
- **Health Monitoring**:
  - Track proxy success/failure rates
  - Disable failing proxies temporarily
  - Re-validate proxies periodically
- **Configuration**: Load proxies from config file or environment variable

**Storage Strategy**:
- **Yes, save entire pages locally** for multiple reasons:
  - Enables offline analysis and reprocessing
  - Allows caching to avoid repeated requests
  - Provides audit trail of content at time of analysis
  - Reduces API/bandwidth costs during iterative testing
  - Avoids re-scraping when proxies rotate

**Storage Format**:
```
data/
├── raw/
│   ├── keyword-slug/
│   │   ├── metadata.json          # Search results metadata
│   │   ├── competitor_1.html       # Full HTML
│   │   ├── competitor_1_text.txt   # Extracted text
│   │   └── ...
├── processed/
│   └── keyword-slug/
│       ├── embeddings.pkl          # Generated embeddings
│       └── analysis.json           # Comparison results
```

### 3. Text Extraction & Preprocessing
**Goals**:
- Extract main content (remove navigation, ads, footers)
- Clean HTML artifacts
- Normalize whitespace and formatting
- Optionally extract structured data (headings, lists, etc.)

**Libraries**:
- BeautifulSoup4 or lxml for HTML parsing
- readability-lxml or newspaper3k for main content extraction
- spaCy for advanced text processing (optional)

### 4. Semantic Analysis (GPU-Accelerated)
**Approach**:
- Generate embeddings for each page's content
- Use sentence transformers (BERT-based models)
- Calculate cosine similarity between your page and competitors

**GPU Considerations**:
- **Windows + GPU**: Use NVIDIA CUDA-enabled Docker container
- **Configurable Compute**:
  - Light mode: Smaller models (all-MiniLM-L6-v2) ~80MB
  - Medium mode: all-mpnet-base-v2 ~420MB
  - Heavy mode: Large models for maximum accuracy
- **Batch Processing**: Process multiple pages in batches to maximize GPU utilization

**Model Selection**:
```python
COMPUTE_PROFILES = {
    'light': {
        'model': 'all-MiniLM-L6-v2',
        'batch_size': 32,
        'device': 'cpu'  # fallback
    },
    'medium': {
        'model': 'all-mpnet-base-v2',
        'batch_size': 16,
        'device': 'cuda'
    },
    'heavy': {
        'model': 'all-roberta-large-v1',
        'batch_size': 8,
        'device': 'cuda'
    }
}
```

### 5. Docker Strategy

**Container Architecture**:
```
┌─────────────────────────────────────┐
│  SEOMining Container                │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Flask/FastAPI Web Interface │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Fetcher Module              │  │
│  │  - ValueSerp API client      │  │
│  │  - Page spider/scraper       │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Analyzer Module             │  │
│  │  - Embedding generation      │  │
│  │  - Similarity calculation    │  │
│  │  - GPU acceleration (CUDA)   │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Storage                     │  │
│  │  - Volume mount for data/    │  │
│  │  - PostgreSQL/SQLite         │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Docker Compose Setup**:
- Base service: Python app with all dependencies
- GPU support: Use `nvidia-docker` runtime
- Persistent volumes: For data storage outside container
- Environment variables: For API keys and configuration

**Windows GPU Considerations**:
- Requires WSL2 with NVIDIA Container Toolkit
- Or native Windows containers with CUDA support
- Test GPU availability at runtime and fallback to CPU if needed

### 6. Workflow Pipeline

```
1. User Input
   ↓
2. ValueSerp API Call → Get Top 10 URLs
   ↓
3. Spider Each URL
   ├─→ Save raw HTML (data/raw/)
   └─→ Extract clean text
   ↓
4. Generate Embeddings (GPU)
   ├─→ Your page embedding
   └─→ Competitor embeddings (batch)
   ↓
5. Calculate Similarities
   ↓
6. Analyze Gaps
   ├─→ Common terms in top results
   ├─→ Missing semantic clusters
   └─→ Content recommendations
   ↓
7. Generate Report
   ├─→ Similarity scores
   ├─→ Word clouds
   ├─→ Suggested improvements
   └─→ Re-optimization testing
```

## Data Flow

```
[Keyword Input] 
    ↓
[ValueSerp API]
    ↓
[Top 10 URLs + Metadata]
    ↓
[Spider/Scraper] ←→ [Cache Check]
    ↓
[Raw HTML Storage]
    ↓
[Text Extraction]
    ↓
[Clean Text Storage]
    ↓
[Embedding Generation] ← [GPU/CPU Toggle]
    ↓
[Similarity Matrix]
    ↓
[Analysis & Recommendations]
    ↓
[Report Generation]
```

## Configuration Management

**Environment Variables** (`.env`):
```bash
# API Keys
VALUESERP_API_KEY=your_key_here

# Compute Settings
COMPUTE_PROFILE=medium  # light, medium, heavy
USE_GPU=true
GPU_DEVICE=0

# Storage
DATA_DIR=/app/data
CACHE_ENABLED=true
CACHE_TTL_DAYS=7

# Docker
DOCKER_GPU_ENABLED=true
```

## Performance Considerations

1. **Caching**: Store fetched pages for N days to avoid re-scraping
2. **Proxy Distribution**: Spread requests across 50 proxies to avoid rate limits
3. **Smart Rate Limiting**: 
   - Per-proxy rate limiting (not global)
   - Respect robots.txt per domain
   - Adaptive delays based on response times
4. **Batch Processing**: Process embeddings in batches for GPU efficiency
5. **Incremental Updates**: Only re-process changed content
6. **Parallel Fetching**: Use async/threading with proxy pool for concurrent URL fetching

## Security & Best Practices

1. **API Keys**: Never commit; use .env files
2. **User Agents**: Identify your bot properly
3. **Robots.txt**: Respect crawling rules
4. **Rate Limits**: Stay within ValueSerp API limits
5. **Data Retention**: Clear old cached data periodically

## Future Enhancements

- Real-time monitoring of ranking changes
- A/B testing different content variations
- Integration with Google Search Console
- Automated content generation suggestions
- Multi-language support
- Competitive tracking over time

