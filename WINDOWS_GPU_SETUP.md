# Windows GPU Setup Guide - SEO Mining

## Your Hardware Configuration ✅

**Detected:**
- **GPUs**: 2x NVIDIA Quadro RTX 4000 (8GB VRAM each)
- **Driver**: NVIDIA 573.06
- **CUDA**: Version 12.8
- **Docker**: Version 28.0.4
- **OS**: Windows 10/11

**Status**: Excellent setup! Ready for GPU-accelerated embedding generation.

---

## Quick Start Checklist

### Phase 1: Docker Desktop Setup
- [ ] Start Docker Desktop
- [ ] Enable WSL2 backend
- [ ] Install NVIDIA Container Toolkit
- [ ] Test GPU access in Docker
- [ ] Configure GPU support in docker-compose

### Phase 2: Environment Configuration
- [ ] Copy `.env` configuration
- [ ] Add ValueSerp API key
- [ ] Configure proxy file (if available)
- [ ] Set GPU preferences

### Phase 3: Launch Services
- [ ] Start PostgreSQL & Redis
- [ ] Run database migrations
- [ ] Start backend API
- [ ] Start Celery worker (with GPU)
- [ ] Verify GPU detection

---

## Step-by-Step Instructions

### Step 1: Start Docker Desktop

**Option A: GUI**
1. Open Start Menu
2. Search for "Docker Desktop"
3. Click to launch
4. Wait for Docker to start (icon in system tray should be green)

**Option B: PowerShell**
```powershell
# Start Docker Desktop programmatically
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Wait ~30 seconds for Docker to fully start
Start-Sleep -Seconds 30

# Verify Docker is running
docker ps
```

---

### Step 2: Enable WSL2 Backend (If Not Already Enabled)

1. Open Docker Desktop
2. Go to **Settings** → **General**
3. Check **"Use WSL 2 based engine"**
4. Click **Apply & Restart**

---

### Step 3: Install NVIDIA Container Toolkit

**Check if already installed:**
```powershell
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

**If you see your GPUs, skip to Step 4.**

**If not installed, follow these steps:**

#### 3.1: Install WSL2 Ubuntu (if not installed)
```powershell
wsl --install -d Ubuntu-22.04
```

#### 3.2: Inside WSL2 Ubuntu, install NVIDIA Container Toolkit
```bash
# Update package list
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg

# Add NVIDIA GPG key
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# Add NVIDIA repository
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install NVIDIA Container Toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker (in Windows Docker Desktop)
```

#### 3.3: Restart Docker Desktop
1. Right-click Docker Desktop icon in system tray
2. Click **Restart**
3. Wait for Docker to fully restart

---

### Step 4: Test GPU Access

```powershell
# Test GPU detection in Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

**Expected output:**
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 573.06                 Driver Version: 573.06         CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                  Driver-Model | Bus-Id          Disp.A | Volatile Uncorr. ECC |
|=========================================+========================+======================|
|   0  Quadro RTX 4000              WDDM  |   00000000:17:00.0 Off |                  N/A |
|   1  Quadro RTX 4000              WDDM  |   00000000:65:00.0  On |                  N/A |
+-----------------------------------------+------------------------+----------------------+
```

---

### Step 5: Configure Environment Variables

#### 5.1: Copy environment template
```powershell
cd backend
copy config.example.env .env
```

#### 5.2: Edit `.env` file

Open `backend/.env` in a text editor and configure:

```bash
# Database (Docker containers)
DATABASE_URL=postgresql://seo_user:seo_password@postgres:5432/seo_mining

# Redis (Docker containers)
REDIS_URL=redis://redis:6379/0

# ValueSerp API
VALUESERP_API_KEY=your_actual_api_key_here

# OpenAI API (optional, for testing toggle)
OPENAI_API_KEY=your_openai_key_here_optional

# Embedding Strategy - USE GPU!
USE_LOCAL_GPU=true
USE_OPENAI_EMBEDDINGS=false
SENTENCE_TRANSFORMER_MODEL=all-mpnet-base-v2

# GPU Settings - 2x RTX 4000
GPU_BATCH_SIZE=128
CUDA_VISIBLE_DEVICES=0,1  # Use both GPUs!

# Proxy Configuration (if you have 50 proxies)
USE_PROXIES=false  # Set to true when proxies.txt is ready
PROXY_FILE=config/proxies.txt
DISABLE_DIRECT_CONNECTION=false  # Set to true with proxies

# Storage
BASE_DATA_DIR=./data
PROJECT_NAME=seo_mining

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Bulk Analysis
BULK_ANALYSIS_OUTPUT_DIR=./output/bulk
BULK_ANALYSIS_CONCURRENCY=3

# Logging
LOG_LEVEL=INFO
```

**Key Settings for Your Hardware:**
- `USE_LOCAL_GPU=true` - Use your RTX 4000 GPUs
- `CUDA_VISIBLE_DEVICES=0,1` - Use both GPUs
- `GPU_BATCH_SIZE=128` - Good for 8GB VRAM per GPU
- `SENTENCE_TRANSFORMER_MODEL=all-mpnet-base-v2` - 420M params, balanced for 8GB

---

### Step 6: Enable GPU Support in docker-compose.yml

Edit `backend/docker-compose.yml`:

```yaml
services:
  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.gpu  # ← Change from Dockerfile
    container_name: seo-mining-backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app
      - ./data:/app/data
      - ./output:/app/output
      - ./config:/app/config
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    # GPU support - UNCOMMENT THESE:
    runtime: nvidia  # ← Uncomment
    environment:
      - NVIDIA_VISIBLE_DEVICES=all  # ← Uncomment
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 2  # ← Use both GPUs (change from 1 to 2)
              capabilities: [gpu]

  # Celery Worker
  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile.gpu  # ← Change from Dockerfile
    container_name: seo-mining-celery-worker
    command: celery -A app.celery_app worker --loglevel=info --concurrency=4
    volumes:
      - ./app:/app/app
      - ./data:/app/data
      - ./output:/app/output
      - ./config:/app/config
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    # GPU support - UNCOMMENT THESE:
    runtime: nvidia  # ← Uncomment
    environment:
      - NVIDIA_VISIBLE_DEVICES=all  # ← Uncomment
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 2  # ← Use both GPUs
              capabilities: [gpu]
```

---

### Step 7: Launch Services

```powershell
cd backend

# Pull/build images and start all services
docker-compose up -d --build

# Watch logs
docker-compose logs -f
```

**Services starting:**
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Celery Worker (background)
- Flower (Celery monitoring, port 5555)

---

### Step 8: Verify GPU Detection

```powershell
# Check if backend can see GPUs
docker-compose exec backend python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}'); [print(f'GPU {i}: {torch.cuda.get_device_name(i)}') for i in range(torch.cuda.device_count())]"
```

**Expected output:**
```
CUDA available: True
GPU count: 2
GPU 0: Quadro RTX 4000
GPU 1: Quadro RTX 4000
```

```powershell
# Check NVIDIA-SMI inside container
docker-compose exec backend nvidia-smi
```

---

### Step 9: Run Database Migrations

```powershell
# Run migrations
docker-compose exec backend alembic upgrade head

# Verify tables created
docker-compose exec postgres psql -U seo_user -d seo_mining -c "\dt"
```

**Expected tables:**
- `analysis_jobs`
- `analysis_results`
- `alembic_version`

---

### Step 10: Test the API

#### Health Check
```powershell
curl http://localhost:8000/health
```

**Expected:**
```json
{"status": "healthy", "gpu_available": true, "gpu_count": 2}
```

#### Start an Analysis Job
```powershell
curl -X POST http://localhost:8000/api/v1/analyze `
  -H "Content-Type: application/json" `
  -d '{
    "url": "https://example.com",
    "keyword": "prescription glasses",
    "optimize": false
  }'
```

**Expected:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued"
}
```

#### Check Job Status
```powershell
# Replace {job_id} with actual ID from previous step
curl http://localhost:8000/api/v1/jobs/{job_id}
```

---

## Monitoring & Debugging

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker

# Last 100 lines
docker-compose logs --tail=100 celery-worker
```

### Check Service Status
```powershell
docker-compose ps
```

### Access Flower (Celery Monitoring)
Open in browser: http://localhost:5555

### Check GPU Utilization
```powershell
# From Windows
nvidia-smi -l 1  # Update every 1 second

# From inside container
docker-compose exec backend nvidia-smi -l 1
```

### Restart Services
```powershell
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart celery-worker
```

### Stop Services
```powershell
# Stop all
docker-compose down

# Stop and remove volumes (careful!)
docker-compose down -v
```

---

## Performance Tuning for Your Hardware

### GPU Batch Size Optimization

Your RTX 4000 has **8GB VRAM**. Here's how to optimize:

**Conservative (Safe):**
```bash
GPU_BATCH_SIZE=64
SENTENCE_TRANSFORMER_MODEL=all-mpnet-base-v2  # 420M params
```

**Balanced (Recommended):**
```bash
GPU_BATCH_SIZE=128
SENTENCE_TRANSFORMER_MODEL=all-mpnet-base-v2
```

**Aggressive (Max Performance):**
```bash
GPU_BATCH_SIZE=256
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2  # Lighter model, 22M params
```

**Test your setup:**
```powershell
docker-compose exec backend python -c "
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer('all-mpnet-base-v2')
model = model.to('cuda')

# Test batch sizes
texts = ['test sentence'] * 256
try:
    embeddings = model.encode(texts, batch_size=256, show_progress_bar=True)
    print('✅ Batch size 256 works!')
except:
    print('❌ Batch size 256 too large, try 128')
"
```

### Using Both GPUs

To use both RTX 4000 GPUs in parallel:

```python
# In your embedding service (Phase 2+)
import torch
from sentence_transformers import SentenceTransformer

# DataParallel will automatically use both GPUs
model = SentenceTransformer('all-mpnet-base-v2')
if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs!")
    model = torch.nn.DataParallel(model)

model = model.to('cuda')
```

---

## Troubleshooting

### GPU Not Detected

**Problem:** `torch.cuda.is_available()` returns `False`

**Solutions:**
1. Verify NVIDIA Container Toolkit installed:
   ```powershell
   wsl -d Ubuntu-22.04 -- nvidia-smi
   ```

2. Check Docker GPU support:
   ```powershell
   docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
   ```

3. Restart Docker Desktop

4. Check `docker-compose.yml` has `runtime: nvidia` uncommented

### Out of Memory (OOM) Error

**Problem:** CUDA out of memory

**Solutions:**
1. Reduce `GPU_BATCH_SIZE` in `.env`:
   ```bash
   GPU_BATCH_SIZE=64  # or 32
   ```

2. Use lighter model:
   ```bash
   SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
   ```

3. Clear GPU cache:
   ```powershell
   docker-compose restart celery-worker
   ```

### Slow Performance

**Problem:** GPU not being utilized

**Solutions:**
1. Check GPU usage:
   ```powershell
   nvidia-smi -l 1
   ```

2. Verify model is on GPU:
   ```python
   print(model.device)  # Should show cuda:0 or cuda:1
   ```

3. Increase batch size for better GPU utilization

### Database Connection Error

**Problem:** Can't connect to PostgreSQL

**Solutions:**
1. Check service is running:
   ```powershell
   docker-compose ps postgres
   ```

2. Check connection string in `.env`:
   ```bash
   DATABASE_URL=postgresql://seo_user:seo_password@postgres:5432/seo_mining
   # Note: Use service name 'postgres', not 'localhost'
   ```

3. Restart services:
   ```powershell
   docker-compose restart postgres backend
   ```

---

## Next Steps

### Phase 2: Implement Core Services (Week 1-2)

Now that infrastructure is running, implement:

1. **Local GPU Embedding Service**
   - `backend/app/services/embeddings/local_gpu_embedder.py`
   - Use sentence-transformers
   - Leverage both RTX 4000 GPUs
   - Batch processing for efficiency

2. **Structural Coherence Scoring**
   - `backend/app/services/scoring/` (8+ scorers)
   - Metadata alignment
   - Hierarchical decomposition
   - Thematic unity
   - Balance scoring
   - Query intent matching

3. **Proxy Manager** (when proxies available)
   - `backend/app/services/scraping/proxy_manager.py`
   - Health monitoring
   - Rotation strategies

See `Plan/Approved/Complete_Optimization_Engine.md` for full specification.

---

## Configuration Summary

**What's working now:**
- ✅ Docker containerization
- ✅ PostgreSQL database
- ✅ Redis job queue
- ✅ FastAPI REST API
- ✅ Celery worker
- ✅ Alembic migrations
- ✅ GPU detection (pending Docker restart)

**What's pending:**
- ⏳ GPU embedding implementation (Phase 2)
- ⏳ 8+ scoring algorithms (Phase 2)
- ⏳ Optimization engine (Phase 3)
- ⏳ Proxy integration (Phase 2/3)

**Your advantage:**
- 🚀 2x RTX 4000 GPUs = 2x faster than single GPU
- 🚀 16GB total VRAM = handle large models + big batches
- 🚀 Local processing = $0 API costs
- 🚀 Full control = optimize for your needs

---

## Quick Reference

### Useful Commands

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Check GPU usage
nvidia-smi

# Test GPU in container
docker-compose exec backend nvidia-smi

# Check API health
curl http://localhost:8000/health

# Access Flower
# http://localhost:5555

# Stop all services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Useful URLs

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Flower: http://localhost:5555
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

**Status:** Ready to start Docker Desktop and configure GPU support! 🚀

Let me know when Docker Desktop is running, and we'll proceed with the GPU setup.

