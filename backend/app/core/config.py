"""Application configuration using pydantic settings.

Adapted from Magic-SEO but extended for our GPU + structural scoring needs.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://seo_user:seo_password@localhost:5432/seo_mining"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # APIs
    VALUESERP_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    
    # Embedding Strategy
    USE_LOCAL_GPU: bool = True
    USE_OPENAI_EMBEDDINGS: bool = False
    OPENAI_MODEL: str = "text-embedding-3-large"
    SENTENCE_TRANSFORMER_MODEL: str = "all-mpnet-base-v2"
    
    # GPU Settings (for Windows machine with NVIDIA)
    GPU_BATCH_SIZE: int = 64
    CUDA_VISIBLE_DEVICES: str = "0"
    
    # Proxy Configuration
    USE_PROXIES: bool = True
    PROXY_FILE: str = "config/proxies.txt"
    DISABLE_DIRECT_CONNECTION: bool = True
    
    # Storage
    BASE_DATA_DIR: str = "./data"
    PROJECT_NAME: str = "default_project"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Bulk Analysis
    BULK_ANALYSIS_OUTPUT_DIR: str = "./output/bulk"
    BULK_ANALYSIS_CONCURRENCY: int = 3
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Scoring Weights (for composite score calculation)
    WEIGHT_ALIGNMENT: float = 0.25
    WEIGHT_COVERAGE: float = 0.25
    WEIGHT_STRUCTURAL: float = 0.15
    WEIGHT_METADATA_ALIGNMENT: float = 0.10
    WEIGHT_HIERARCHICAL_DECOMP: float = 0.10
    WEIGHT_THEMATIC_UNITY: float = 0.05
    WEIGHT_BALANCE: float = 0.05
    WEIGHT_QUERY_INTENT: float = 0.05
    
    # Optimization Settings
    MIN_IMPROVEMENT_THRESHOLD: float = 0.01  # Keep changes that improve score by at least this much
    MAX_OPTIMIZATION_ITERATIONS: int = 50
    CACHE_HIT_RATE_TARGET: float = 0.90  # Target 90%+ cache hit rate
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

