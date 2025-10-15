# SEO Mining

A Python-based toolkit for semantic relevance optimization and SEO content analysis.

## Overview

This project helps you optimize your web pages by comparing their semantic relevance against top-ranking search results. Using embeddings and natural language processing, it identifies opportunities to improve your content's ranking potential.

## Project Goals

- **Semantic Analysis**: Compare your content against top search results using AI embeddings
- **Content Optimization**: Identify and suggest improvements based on high-ranking pages
- **Automation**: Streamline the process of iterative content improvement

## Getting Started

See `/Plan/SEOMiningPlan.md` for the detailed implementation roadmap.

## Key Features

- **ValueSerp Integration**: Fetch top 10 search results for any keyword
- **Intelligent Crawling**: Spider and store competitor pages locally through 50 rotating proxies
- **No Direct Connections**: All requests routed through proxy pool for anonymity and rate limit avoidance
- **Configurable Storage**: Full control over where data is saved - supports absolute paths, relative paths, and environment variables
- **Organized File Structure**: Automatic organization by project and keyword with separate raw/processed/reports directories
- **GPU-Accelerated Analysis**: Leverage CUDA for fast semantic embedding generation
- **Docker Containerized**: Consistent deployment across environments with volume mapping
- **Semantic Comparison**: Compare your content against top-ranking pages
- **Structural Coherence Scoring**: Measure APA-style quality (metadata alignment, H1→H2→H3 logic, thematic unity)
- **Query Intent Matching**: Ensure page structure matches what the query implies
- **Iterative Optimization**: Test content changes and measure improvements

## Technology Stack

### Core Services
- **Search API**: ValueSerp (SERP data)
- **Crawling**: Custom scraper + SEO Screaming Frog + Browserbase
- **Proxies**: 50 rotating proxies (no direct connections)
- **AI**: OpenAI GPT-5 (keyword extraction), OpenAI embeddings

### Backend Infrastructure
- **Database**: PostgreSQL (job/result persistence)
- **Job Queue**: Celery + Redis (background task processing)
- **Monitoring**: Flower (Celery monitoring UI)
- **Migrations**: Alembic (database schema management)

### Analysis & ML
- **Embeddings**: Sentence Transformers (BERT-based), OpenAI embeddings
- **Clustering**: HDBSCAN, scikit-learn
- **GPU Support**: NVIDIA CUDA via Docker (optional local embeddings)

### Deployment
- **Container**: Docker with GPU passthrough
- **Orchestration**: docker-compose (PostgreSQL + Redis + Backend + Celery Worker + Flower)
- **Storage**: Configurable local filesystem (absolute/relative/env var paths)

## Project Structure

```
SEO Mining/
├── Plan/                      # Project planning and documentation
│   ├── SEOMiningPlan.md       # High-level strategy
│   ├── Architecture.md        # System architecture
│   ├── Implementation_Phases.md # Development roadmap
│   ├── Proxy_Strategy.md      # Proxy pool management
│   ├── Storage_Configuration.md # Storage & file organization
│   └── ValueSerp_API_Documentation.md # API integration details
├── config/                    # Configuration files
│   └── proxies.txt            # 50 proxy addresses (not committed)
├── fetch/                     # (Coming soon) Data collection modules
│   ├── valueserp_client.py    # API client
│   └── page_scraper.py        # Web scraper
├── analyze/                   # (Coming soon) Content analysis tools
│   ├── text_extractor.py      # HTML to text
│   ├── embedder.py            # Embedding generation
│   └── similarity.py          # Similarity calculation
├── report/                    # (Coming soon) Reporting and visualization
├── utils/                     # (Coming soon) Shared utilities
│   ├── storage.py             # File management
│   └── gpu_utils.py           # GPU detection
├── data/                      # Local storage (gitignored)
│   ├── raw/                   # Raw HTML pages
│   └── processed/             # Embeddings and results
├── .env.example               # Configuration template
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container definition
└── docker-compose.yml         # Docker orchestration
```

## Installation

### Prerequisites
- Docker Desktop (for containerized deployment)
- NVIDIA GPU + CUDA drivers (for GPU acceleration)
- ValueSerp API key
- Windows 10/11 (current setup) or Mac/Linux

### Quick Start (Windows)

**Option 1: Automated Setup (Recommended)**
```powershell
# Run the setup script
.\start-windows.ps1
```

**Option 2: Manual Setup**
1. Start Docker Desktop
2. Copy `.env` configuration:
   ```powershell
   cd backend
   copy config.example.env .env
   # Edit .env and add your ValueSerp API key
   ```
3. Start all services:
   ```powershell
   docker-compose up -d --build
   ```
4. Run database migrations:
   ```powershell
   docker-compose exec backend alembic upgrade head
   ```
5. Test the API:
   ```powershell
   curl http://localhost:8000/health
   ```

For detailed GPU setup instructions, see `WINDOWS_GPU_SETUP.md`

## License

(To be determined)

