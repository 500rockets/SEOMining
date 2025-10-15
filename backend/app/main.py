"""Main FastAPI application.

Entry point for the SEO Mining backend API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.core.config import settings
from app.api.routes import analysis

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="SEO Mining API",
    description="Advanced SEO Optimization Engine with Structural Coherence Scoring",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("seo_mining_startup", version="0.1.0")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("seo_mining_shutdown")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SEO Mining API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with GPU detection"""
    health_status = {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check in Phase 2
        "redis": "connected",  # TODO: Add actual Redis check in Phase 2
    }
    
    # Check GPU availability
    try:
        import torch
        health_status["gpu_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            health_status["gpu_count"] = torch.cuda.device_count()
            health_status["gpu_devices"] = [
                torch.cuda.get_device_name(i) 
                for i in range(torch.cuda.device_count())
            ]
    except Exception as e:
        health_status["gpu_available"] = False
        health_status["gpu_error"] = str(e)
    
    return health_status

