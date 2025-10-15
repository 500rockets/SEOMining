# SEO Mining - Windows Quick Start Script
# Run this script to set up and start the SEO Mining backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SEO Mining - Windows Quick Start    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
}

# Step 1: Check Docker
Write-Host "[1/8] Checking Docker..." -ForegroundColor Yellow
if (-not (Test-Command docker)) {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    Write-Host "   Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}

$dockerVersion = docker --version
Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green

# Step 2: Check if Docker is running
Write-Host "[2/8] Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✅ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Docker daemon not running. Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
    Write-Host "   Waiting 30 seconds for Docker to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    try {
        docker ps | Out-Null
        Write-Host "✅ Docker daemon started successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker daemon failed to start. Please start Docker Desktop manually." -ForegroundColor Red
        exit 1
    }
}

# Step 3: Check NVIDIA GPU
Write-Host "[3/8] Checking NVIDIA GPU..." -ForegroundColor Yellow
if (Test-Command nvidia-smi) {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>$null
    if ($gpuInfo) {
        Write-Host "✅ NVIDIA GPU(s) detected:" -ForegroundColor Green
        $gpuInfo | ForEach-Object { Write-Host "   $_" -ForegroundColor Green }
    } else {
        Write-Host "⚠️  nvidia-smi found but no GPUs detected" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  nvidia-smi not found. GPU support may not be available." -ForegroundColor Yellow
    Write-Host "   Install NVIDIA drivers from: https://www.nvidia.com/Download/index.aspx" -ForegroundColor Yellow
}

# Step 4: Test GPU access in Docker
Write-Host "[4/8] Testing GPU access in Docker..." -ForegroundColor Yellow
try {
    $gpuTest = docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker can access GPU(s)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Docker cannot access GPU. Install NVIDIA Container Toolkit." -ForegroundColor Yellow
        Write-Host "   See WINDOWS_GPU_SETUP.md for instructions" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not test GPU access in Docker" -ForegroundColor Yellow
}

# Step 5: Check if .env exists
Write-Host "[5/8] Checking configuration..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  .env not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item "backend\config.example.env" "backend\.env"
    Write-Host "✅ Created backend\.env from template" -ForegroundColor Green
    Write-Host "   ⚠️  IMPORTANT: Edit backend\.env and add your ValueSerp API key!" -ForegroundColor Yellow
    Write-Host "" 
    $response = Read-Host "   Do you want to edit .env now? (y/n)"
    if ($response -eq "y") {
        notepad "backend\.env"
    }
} else {
    Write-Host "✅ Configuration file exists: backend\.env" -ForegroundColor Green
}

# Step 6: Check if proxies.txt exists
Write-Host "[6/8] Checking proxy configuration..." -ForegroundColor Yellow
if (-not (Test-Path "config\proxies.txt")) {
    Write-Host "⚠️  config\proxies.txt not found. Proxies disabled." -ForegroundColor Yellow
    Write-Host "   Create config\proxies.txt if you have proxies to use." -ForegroundColor Yellow
} else {
    $proxyCount = (Get-Content "config\proxies.txt" | Measure-Object -Line).Lines
    Write-Host "✅ Found config\proxies.txt with $proxyCount proxies" -ForegroundColor Green
}

# Step 7: Build and start services
Write-Host "[7/8] Building and starting services..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes on first run..." -ForegroundColor Cyan

Push-Location backend
try {
    docker-compose up -d --build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services started successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start services. Check logs with: docker-compose logs" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} catch {
    Write-Host "❌ Error starting services: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Wait for services to be ready
Write-Host "   Waiting for services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Step 8: Verify services
Write-Host "[8/8] Verifying services..." -ForegroundColor Yellow

# Check service status
$services = docker-compose ps --format json | ConvertFrom-Json
$healthyServices = 0
$totalServices = 0

foreach ($service in $services) {
    $totalServices++
    $serviceName = $service.Service
    $state = $service.State
    
    if ($state -eq "running") {
        Write-Host "   ✅ $serviceName is running" -ForegroundColor Green
        $healthyServices++
    } else {
        Write-Host "   ❌ $serviceName is not running (state: $state)" -ForegroundColor Red
    }
}

Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Setup Complete!                      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($healthyServices -eq $totalServices) {
    Write-Host "✅ All $totalServices services are running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Test the API:  curl http://localhost:8000/health" -ForegroundColor White
    Write-Host "2. View API docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "3. Monitor Celery: http://localhost:5555" -ForegroundColor White
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Cyan
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   docker-compose logs -f" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop services:" -ForegroundColor Cyan
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   docker-compose down" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️  Some services failed to start ($healthyServices/$totalServices running)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Check logs:" -ForegroundColor Cyan
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   docker-compose logs" -ForegroundColor White
    Write-Host ""
}

# Offer to run migrations
Write-Host "Do you want to run database migrations now? (y/n): " -ForegroundColor Cyan -NoNewline
$migrationResponse = Read-Host
if ($migrationResponse -eq "y") {
    Write-Host ""
    Write-Host "Running database migrations..." -ForegroundColor Yellow
    Push-Location backend
    docker-compose exec backend alembic upgrade head
    Pop-Location
    Write-Host "✅ Migrations complete" -ForegroundColor Green
}

Write-Host ""
Write-Host "For detailed setup instructions, see WINDOWS_GPU_SETUP.md" -ForegroundColor Cyan
Write-Host "For development progress, see PROGRESS.md" -ForegroundColor Cyan
Write-Host ""

