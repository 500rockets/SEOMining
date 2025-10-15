# SEO Mining - Quick Reference

## 🚀 Common Commands

### Starting & Stopping

```powershell
# Quick start (automated)
.\start-windows.ps1

# Start services manually
cd backend
docker-compose up -d

# Start with rebuild
docker-compose up -d --build

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Restart specific service
docker-compose restart backend
docker-compose restart celery-worker
```

### Viewing Logs

```powershell
cd backend

# All services, follow mode
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 backend

# Since timestamp
docker-compose logs --since 2024-10-15T10:00:00
```

### GPU Monitoring

```powershell
# Watch GPU usage (updates every 1 second)
nvidia-smi -l 1

# Check GPU in Docker container
cd backend
docker-compose exec backend nvidia-smi

# Test PyTorch GPU access
docker-compose exec backend python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPUs: {torch.cuda.device_count()}'); [print(f'GPU {i}: {torch.cuda.get_device_name(i)}') for i in range(torch.cuda.device_count())]"
```

### Database Operations

```powershell
cd backend

# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Rollback migration
docker-compose exec backend alembic downgrade -1

# Check current version
docker-compose exec backend alembic current

# Access PostgreSQL
docker-compose exec postgres psql -U seo_user -d seo_mining

# List tables
docker-compose exec postgres psql -U seo_user -d seo_mining -c "\dt"

# Backup database
docker-compose exec postgres pg_dump -U seo_user seo_mining > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U seo_user -d seo_mining
```

### Redis Operations

```powershell
cd backend

# Access Redis CLI
docker-compose exec redis redis-cli

# Check Redis info
docker-compose exec redis redis-cli info

# Monitor Redis commands
docker-compose exec redis redis-cli monitor

# Clear all Redis data (careful!)
docker-compose exec redis redis-cli FLUSHALL
```

### API Testing

```powershell
# Health check
curl http://localhost:8000/health

# Health check with GPU info
curl http://localhost:8000/health | ConvertFrom-Json | Format-List

# API documentation
start http://localhost:8000/docs

# Start analysis job
curl -X POST http://localhost:8000/api/v1/analyze `
  -H "Content-Type: application/json" `
  -d '{
    "url": "https://example.com",
    "keyword": "test keyword",
    "optimize": false
  }'

# Check job status (replace {job_id})
curl http://localhost:8000/api/v1/jobs/{job_id}

# Get job results
curl http://localhost:8000/api/v1/jobs/{job_id}/results
```

### Celery Operations

```powershell
cd backend

# Check Celery worker status
docker-compose exec celery-worker celery -A app.celery_app inspect active

# Check registered tasks
docker-compose exec celery-worker celery -A app.celery_app inspect registered

# Check worker stats
docker-compose exec celery-worker celery -A app.celery_app inspect stats

# Purge all tasks
docker-compose exec celery-worker celery -A app.celery_app purge

# Flower monitoring UI
start http://localhost:5555
```

### Service Status

```powershell
cd backend

# Check all services
docker-compose ps

# Detailed service info
docker-compose ps --format json | ConvertFrom-Json | Format-List

# Check resource usage
docker stats

# Inspect specific service
docker inspect seo-mining-backend
```

---

## 📊 Monitoring URLs

| Service | URL | Description |
|---------|-----|-------------|
| API Docs (Swagger) | http://localhost:8000/docs | Interactive API documentation |
| API Docs (ReDoc) | http://localhost:8000/redoc | Alternative API docs |
| Health Check | http://localhost:8000/health | Service health + GPU status |
| Flower | http://localhost:5555 | Celery task monitoring |
| PostgreSQL | localhost:5432 | Database (use psql or GUI) |
| Redis | localhost:6379 | Cache/queue (use redis-cli) |

---

## 🔧 Troubleshooting

### Docker Desktop Not Running

```powershell
# Start Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Wait for it to start
Start-Sleep -Seconds 30

# Verify
docker ps
```

### GPU Not Detected

```powershell
# Check NVIDIA driver
nvidia-smi

# Test GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Check docker-compose.yml has GPU support enabled
# Look for: runtime: nvidia

# Restart Docker Desktop
# Right-click system tray icon → Restart
```

### Service Won't Start

```powershell
cd backend

# Check logs for errors
docker-compose logs service-name

# Rebuild service
docker-compose up -d --build service-name

# Remove and recreate
docker-compose rm -f service-name
docker-compose up -d service-name
```

### Database Connection Error

```powershell
cd backend

# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# Verify connection string in .env
# Should be: postgresql://seo_user:seo_password@postgres:5432/seo_mining
```

### Port Already in Use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# Change "8000:8000" to "8001:8000"
```

### Out of Disk Space

```powershell
# Remove old containers
docker container prune -f

# Remove old images
docker image prune -a -f

# Remove unused volumes
docker volume prune -f

# Full cleanup (careful!)
docker system prune -a --volumes -f
```

### Clear All Data (Fresh Start)

```powershell
cd backend

# Stop everything
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Rebuild from scratch
docker-compose up -d --build
```

---

## 📁 File Locations

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| Environment | `backend/.env` | API keys, DB settings, GPU config |
| Proxies | `config/proxies.txt` | 50 proxy addresses |
| Docker Compose | `backend/docker-compose.yml` | Service orchestration |
| API Routes | `backend/app/api/routes/` | Endpoint definitions |
| Database Models | `backend/app/db/models.py` | Schema definitions |

### Data Directories

| Directory | Location | Purpose |
|-----------|----------|---------|
| Raw Data | `backend/data/raw/` | Scraped HTML pages |
| Processed | `backend/data/processed/` | Embeddings, analysis |
| Output | `backend/output/` | Reports, exports |
| Config | `backend/config/` | Proxy list, settings |
| Migrations | `backend/alembic/versions/` | Database migrations |

---

## 🎯 Development Workflow

### 1. Make Code Changes

Edit files in `backend/app/`

### 2. Test Locally (if running with --reload)

Changes auto-reload for:
- `backend/app/` directory (mounted as volume)

No reload needed unless you change:
- Dependencies (`requirements.txt`)
- Docker config (`Dockerfile`, `docker-compose.yml`)
- Environment variables (`.env`)

### 3. Rebuild After Dependency Changes

```powershell
cd backend
docker-compose down
docker-compose up -d --build
```

### 4. Check Logs

```powershell
docker-compose logs -f backend
```

### 5. Test API

```powershell
curl http://localhost:8000/health
```

---

## 🔬 Testing Commands

### Unit Tests (Phase 2+)

```powershell
cd backend

# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_embeddings.py

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test
docker-compose exec backend pytest tests/test_embeddings.py::test_gpu_available
```

### Integration Tests (Phase 2+)

```powershell
# Full analysis workflow
curl -X POST http://localhost:8000/api/v1/analyze `
  -H "Content-Type: application/json" `
  -d '{
    "url": "https://example.com",
    "keyword": "test",
    "optimize": false
  }'

# Check Celery task picked up
docker-compose logs -f celery-worker
```

---

## 📖 Documentation

### Quick Links

- **Setup**: `WINDOWS_GPU_SETUP.md` - Detailed GPU setup instructions
- **Progress**: `PROGRESS.md` - Development status and phases
- **Strategy**: `IMPLEMENTATION_STRATEGY.md` - Why separate repo, what to copy
- **Engine**: `Plan/Approved/Complete_Optimization_Engine.md` - How everything works
- **Scoring**: `Plan/Approved/Structural_Coherence_Scoring.md` - 8+ algorithms
- **Hashing**: `Plan/Approved/Hashing_Optimization_Strategy.md` - Optimization engine

### API Documentation

```powershell
# Interactive docs (Swagger)
start http://localhost:8000/docs

# Alternative docs (ReDoc)
start http://localhost:8000/redoc
```

---

## 🚨 Emergency Commands

### Service Crashed

```powershell
cd backend
docker-compose restart
```

### Complete Reset

```powershell
cd backend
docker-compose down -v
docker-compose up -d --build
docker-compose exec backend alembic upgrade head
```

### GPU Memory Full

```powershell
# Restart GPU-using services
cd backend
docker-compose restart backend celery-worker

# Or restart entire system
shutdown /r /t 0
```

### Check What's Using GPU

```powershell
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
```

---

## 📊 Performance Monitoring

### GPU Utilization

```powershell
# Real-time monitoring
nvidia-smi -l 1

# Log to file
nvidia-smi dmon -s pucvmet -o TD -f gpu_log.csv
```

### Docker Stats

```powershell
# All containers
docker stats

# Specific container
docker stats seo-mining-backend
```

### Database Size

```powershell
cd backend
docker-compose exec postgres psql -U seo_user -d seo_mining -c "SELECT pg_size_pretty(pg_database_size('seo_mining'));"
```

### Redis Memory

```powershell
cd backend
docker-compose exec redis redis-cli info memory
```

---

## 🎓 Next Steps

### Phase 2 Implementation

See `PROGRESS.md` for detailed task list:

1. Implement GPU embedding service
2. Implement 8+ scoring algorithms
3. Build scraping infrastructure
4. Wire analysis workflow

### Learning Resources

- FastAPI: https://fastapi.tiangolo.com/
- Celery: https://docs.celeryproject.org/
- Sentence Transformers: https://www.sbert.net/
- PostgreSQL: https://www.postgresql.org/docs/
- Docker: https://docs.docker.com/

---

**Quick start:** `.\start-windows.ps1`  
**Detailed setup:** `WINDOWS_GPU_SETUP.md`  
**Progress tracking:** `PROGRESS.md`  
**This reference:** `QUICK_REFERENCE.md`

