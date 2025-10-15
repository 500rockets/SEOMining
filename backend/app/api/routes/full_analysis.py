"""
API endpoints for Full Analysis Pipeline
SERP → Scrape → Embed → Score → Insights
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import structlog

from app.services.analysis import get_analysis_pipeline

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/full-analysis", tags=["full-analysis"])


# Request/Response Models
class FullAnalysisRequest(BaseModel):
    """Request model for full competitive analysis"""
    query: str = Field(..., description="Target search query")
    target_url: Optional[str] = Field(None, description="Your URL to analyze")
    analyze_top_n: int = Field(10, ge=1, le=20, description="Number of competitors to analyze")
    location: str = Field("United States", description="Geographic location for SERP")
    use_proxies: bool = Field(True, description="Use proxy rotation for scraping")


class CompetitorResult(BaseModel):
    """Single competitor analysis result"""
    position: int
    url: str
    title: str
    composite_score: float
    seo_score: float
    content_length: int
    chunk_count: int


class FullAnalysisResponse(BaseModel):
    """Response model for full analysis"""
    query: str
    target_url: Optional[str]
    target_score: Optional[Dict]
    competitors: List[CompetitorResult]
    insights: Dict
    recommendations: List[str]


@router.post("/analyze", response_model=FullAnalysisResponse)
async def full_analysis(request: FullAnalysisRequest):
    """
    Complete SEO competitive analysis pipeline
    
    Workflow:
    1. Fetch SERP results for query
    2. Scrape top N competitor URLs (with proxy rotation)
    3. Extract and chunk content
    4. Generate embeddings for semantic analysis
    5. Score all content across 8 dimensions
    6. Generate competitive insights
    7. Provide actionable recommendations
    
    This is the complete end-to-end analysis!
    """
    try:
        logger.info(
            "full_analysis_request",
            query=request.query,
            target_url=request.target_url,
            analyze_top_n=request.analyze_top_n
        )
        
        # Get pipeline instance
        pipeline = get_analysis_pipeline(
            proxy_file="/app/config/proxies.txt" if request.use_proxies else None
        )
        
        # Run complete analysis
        result = await pipeline.analyze_query(
            query=request.query,
            target_url=request.target_url,
            analyze_top_n=request.analyze_top_n,
            location=request.location
        )
        
        # Convert to response format
        competitors = [
            CompetitorResult(
                position=c.position,
                url=c.url,
                title=c.title,
                composite_score=c.score.composite_score,
                seo_score=c.score.seo_score,
                content_length=c.content_length,
                chunk_count=c.chunk_count
            )
            for c in result.competitors
        ]
        
        target_score_dict = None
        if result.target_score:
            target_score_dict = {
                'metadata_alignment': result.target_score.metadata_alignment,
                'hierarchical_decomposition': result.target_score.hierarchical_decomposition,
                'thematic_unity': result.target_score.thematic_unity,
                'balance': result.target_score.balance,
                'query_intent': result.target_score.query_intent,
                'structural_coherence': result.target_score.structural_coherence,
                'composite_score': result.target_score.composite_score,
                'seo_score': result.target_score.seo_score,
                'recommendations': result.target_score.recommendations
            }
        
        logger.info(
            "full_analysis_complete",
            query=request.query,
            competitors_analyzed=len(competitors)
        )
        
        return FullAnalysisResponse(
            query=result.query,
            target_url=result.target_url,
            target_score=target_score_dict,
            competitors=competitors,
            insights=result.insights,
            recommendations=result.recommendations
        )
        
    except Exception as e:
        logger.error("full_analysis_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/example")
async def get_example_request():
    """
    Get example request for full analysis
    
    Useful for understanding the API structure
    """
    return {
        "example_request": {
            "query": "best SEO tools 2025",
            "target_url": "https://yoursite.com/seo-tools",
            "analyze_top_n": 10,
            "location": "United States",
            "use_proxies": True
        },
        "note": "The analysis will take 1-3 minutes depending on the number of competitors",
        "steps": [
            "1. Fetch SERP results from API",
            "2. Scrape competitor pages with proxy rotation",
            "3. Extract clean content with Trafilatura",
            "4. Chunk content into semantic units",
            "5. Generate embeddings on GPU",
            "6. Score all content across 8 dimensions",
            "7. Generate competitive insights",
            "8. Provide actionable recommendations"
        ]
    }


@router.get("/status")
async def analysis_status():
    """
    Get analysis pipeline status
    
    Check if all services are operational
    """
    status_info = {
        "pipeline": "operational",
        "services": {}
    }
    
    try:
        # Check each service
        from app.services.embeddings import get_embedding_service
        from app.services.scraping import get_scraping_service
        from app.services.scoring import get_scoring_service
        from app.services.serp import get_serp_service
        
        # Embeddings
        try:
            emb_service = get_embedding_service()
            device_info = emb_service.get_device_info()
            status_info["services"]["embeddings"] = {
                "status": "operational",
                "device": device_info['device'],
                "gpu_count": device_info.get('gpu_count', 0)
            }
        except Exception as e:
            status_info["services"]["embeddings"] = {"status": "error", "error": str(e)}
        
        # Scraping
        try:
            scrape_service = get_scraping_service(proxy_file="/app/config/proxies.txt")
            status_info["services"]["scraping"] = {
                "status": "operational",
                "proxy_count": len(scrape_service.proxy_manager.proxies) if scrape_service.proxy_manager else 0
            }
        except Exception as e:
            status_info["services"]["scraping"] = {"status": "error", "error": str(e)}
        
        # Scoring
        try:
            score_service = get_scoring_service()
            status_info["services"]["scoring"] = {"status": "operational"}
        except Exception as e:
            status_info["services"]["scoring"] = {"status": "error", "error": str(e)}
        
        # SERP
        try:
            serp_service = get_serp_service()
            status_info["services"]["serp"] = {
                "status": "operational",
                "has_api_key": bool(serp_service.api_key)
            }
        except Exception as e:
            status_info["services"]["serp"] = {"status": "error", "error": str(e)}
        
        return status_info
        
    except Exception as e:
        logger.error("status_check_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )

