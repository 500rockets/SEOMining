"""Analysis API endpoints.

Adapted from Magic-SEO's bulk_analysis.py but for single-page and batch analysis.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import Optional
import structlog

from app.db.database import get_db
from app.db.models import AnalysisJob, AnalysisResult, JobStatus
from app.tasks.analysis_task import analyze_page_task

logger = structlog.get_logger()

router = APIRouter()


# ============================================================
# Request/Response Models
# ============================================================

class AnalyzePageRequest(BaseModel):
    """Request to analyze a single page"""
    url: HttpUrl
    keyword: str
    optimize: bool = True  # Whether to run optimization loop
    max_iterations: Optional[int] = 50


class AnalyzePageResponse(BaseModel):
    """Response with job ID"""
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    target_url: str
    target_keyword: str
    progress_percent: int
    created_at: str
    updated_at: str
    error_message: Optional[str] = None


# ============================================================
# Endpoints
# ============================================================

@router.post("/analyze", response_model=AnalyzePageResponse)
async def analyze_page(
    request: AnalyzePageRequest,
    db: Session = Depends(get_db)
):
    """
    Start analyzing a page.
    
    This creates a job and queues it for processing by Celery workers.
    """
    try:
        # Create analysis job
        job = AnalysisJob(
            target_url=str(request.url),
            target_keyword=request.keyword,
            status=JobStatus.PENDING,
            total_steps=10 if request.optimize else 5,  # Estimate based on optimization
            completed_steps=0,
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(
            "analysis_job_created",
            job_id=str(job.id),
            url=request.url,
            keyword=request.keyword,
            optimize=request.optimize,
        )
        
        # Queue task for processing
        analyze_page_task.apply_async(
            args=[str(job.id), str(request.url), request.keyword],
            kwargs={"optimize": request.optimize, "max_iterations": request.max_iterations}
        )
        
        return AnalyzePageResponse(
            job_id=str(job.id),
            status=job.status.value,
            message=f"Analysis job created. Poll /api/v1/jobs/{job.id} for status.",
        )
        
    except Exception as e:
        logger.error("failed_to_create_job", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create analysis job: {str(e)}")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get the status of an analysis job.
    
    Poll this endpoint to check progress.
    """
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return JobStatusResponse(
            job_id=str(job.id),
            status=job.status.value,
            target_url=job.target_url,
            target_keyword=job.target_keyword,
            progress_percent=job.progress_percent,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
            error_message=job.error_message,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("failed_to_get_job_status", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/jobs/{job_id}/results")
async def get_job_results(job_id: str, db: Session = Depends(get_db)):
    """
    Get the detailed results of a completed analysis job.
    
    Returns all scores, gaps, recommendations, etc.
    """
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Job is not completed yet. Current status: {job.status.value}"
            )
        
        # Get results
        results = db.query(AnalysisResult).filter(AnalysisResult.job_id == job_id).all()
        
        return {
            "job_id": str(job.id),
            "status": job.status.value,
            "target_url": job.target_url,
            "target_keyword": job.target_keyword,
            "results": [result.to_dict() for result in results],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("failed_to_get_results", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    """
    Delete an analysis job and its results.
    """
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        db.delete(job)
        db.commit()
        
        logger.info("job_deleted", job_id=job_id)
        
        return {"message": f"Job {job_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("failed_to_delete_job", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")

