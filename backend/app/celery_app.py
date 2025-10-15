"""Celery application for background task processing.

Adapted from Magic-SEO's celery_app.py pattern.
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "seo_mining",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # Soft limit at 55 minutes
    worker_prefetch_multiplier=1,  # Take one task at a time
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)
)

# Auto-discover tasks from tasks module
celery_app.autodiscover_tasks(["app.tasks"])

