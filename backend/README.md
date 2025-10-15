# SEO Mining Backend - Phase 1 (Infrastructure)

## Overview

Phase 1 infrastructure setup for the SEO Mining optimization engine. This provides the foundation for:
- Database (PostgreSQL)
- Job queue (Celery + Redis)
- REST API (FastAPI)
- Docker containerization
- Ready for GPU integration on Windows machine

## Quick Start (Mac - Development)

### 1. Install Requirements

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp config.example.env .env
# Edit .env with your ValueSerp API key
```

### 3. Start Services with Docker

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Wait for services to be healthy
docker-compose ps
```

### 4. Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial tables"

# Apply migration
alembic upgrade head
```

### 5. Start Backend (Development)

```bash
# Terminal 1: API Server
uvicorn app.main:app --reload

# Terminal 2: Celery Worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Flower (Celery monitoring)
celery -A app.celery_app flower
```

### 6. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Start an analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "keyword": "prescription glasses",
    "optimize": false
  }'

# Check job status (use job_id from previous response)
curl http://localhost:8000/api/v1/jobs/{job_id}

# Get results
curl http://localhost:8000/api/v1/jobs/{job_id}/results
```

---

## Windows GPU Setup (Phase 2+)

When ready to move to Windows machine with NVIDIA GPU:

### 1. Install Docker Desktop with WSL2

- Install Docker Desktop for Windows
- Enable WSL2 backend
- Install NVIDIA Container Toolkit

### 2. Update docker-compose.yml

Uncomment the GPU sections:

```yaml
services:
  backend:
    # Change to Dockerfile.gpu
    dockerfile: Dockerfile.gpu
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 3. Update .env

```bash
USE_LOCAL_GPU=true
USE_OPENAI_EMBEDDINGS=false
CUDA_VISIBLE_DEVICES=0
```

### 4. Build and Run

```bash
docker-compose up --build
```

### 5. Verify GPU Access

```bash
docker-compose exec backend python -c "import torch; print(torch.cuda.is_available())"
# Should print: True

docker-compose exec backend nvidia-smi
# Should show your GPU
```

---

## Project Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   ├── env.py                 # Alembic configuration
│   └── script.py.mako         # Migration template
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI application
│   ├── celery_app.py          # Celery configuration
│   ├── api/
│   │   └── routes/
│   │       └── analysis.py    # Analysis endpoints
│   ├── core/
│   │   └── config.py          # Settings
│   ├── db/
│   │   ├── database.py        # DB connection
│   │   └── models.py          # SQLAlchemy models (8+ scores)
│   └── tasks/
│       └── analysis_task.py   # Celery tasks (skeleton)
├── config.example.env         # Environment template
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # CPU version (Mac)
├── Dockerfile.gpu             # GPU version (Windows)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Phase 1 Status: ✅ COMPLETE

What's implemented:
- ✅ Database models (8+ scoring dimensions)
- ✅ Celery job queue
- ✅ FastAPI REST API
- ✅ Docker setup (CPU and GPU versions)
- ✅ Alembic migrations
- ✅ Basic analysis workflow

What's next (Phase 2-3):
- ⏳ Local GPU embedding service
- ⏳ 8+ scoring algorithms
- ⏳ Structural coherence analysis
- ⏳ Hashing optimization engine
- ⏳ 50-proxy scraping infrastructure

---

## API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Flower (Celery):** http://localhost:5555

---

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

---

## Troubleshooting

### Database connection error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U seo_user -d seo_mining -c "\dt"
```

### Celery worker not picking up tasks

```bash
# Check Redis is running
docker-compose ps redis

# Check Redis connection
redis-cli ping
```

### GPU not detected (Windows)

```bash
# Verify NVIDIA drivers
nvidia-smi

# Verify Docker GPU support
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

---

## Next Steps

1. ✅ **Phase 1 Complete:** Infrastructure ready
2. **Move to Windows:** Transfer to GPU machine
3. **Phase 2:** Implement embedding + scoring services
4. **Phase 3:** Build optimization engine
5. **Phase 4:** Test with real pages and validate results

Ready for Phase 2 when you are! 🚀

