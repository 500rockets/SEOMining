"""
API endpoints for Scoring Service
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import structlog

from app.services.scoring import get_scoring_service

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/scoring", tags=["scoring"])


# Request/Response Models
class ScoreContentRequest(BaseModel):
    """Request model for content scoring"""
    text: str = Field(..., description="Content text to score")
    title: Optional[str] = Field(None, description="Content title")
    description: Optional[str] = Field(None, description="Meta description")
    query: Optional[str] = Field(None, description="Target search query")


class ContentScoreResponse(BaseModel):
    """Response model for content scoring"""
    metadata_alignment: float
    hierarchical_decomposition: float
    thematic_unity: float
    balance: float
    query_intent: float
    structural_coherence: float
    composite_score: float
    seo_score: float
    details: Dict
    recommendations: List[str]


@router.post("/score", response_model=ContentScoreResponse)
async def score_content(request: ScoreContentRequest):
    """
    Score content using 8-dimensional analysis
    
    Returns comprehensive scoring across all dimensions:
    - Metadata Alignment
    - Hierarchical Decomposition
    - Thematic Unity
    - Balance
    - Query Intent
    - Structural Coherence
    - Composite Score (weighted)
    - SEO Score (specialized)
    """
    try:
        service = get_scoring_service()
        
        # Prepare content dict
        content = {
            'text': request.text,
            'title': request.title or '',
            'description': request.description or ''
        }
        
        # Score content
        logger.info(
            "scoring_content_request",
            text_length=len(request.text),
            has_query=bool(request.query)
        )
        
        score = service.score_content(
            content=content,
            query=request.query
        )
        
        return ContentScoreResponse(
            metadata_alignment=score.metadata_alignment,
            hierarchical_decomposition=score.hierarchical_decomposition,
            thematic_unity=score.thematic_unity,
            balance=score.balance,
            query_intent=score.query_intent,
            structural_coherence=score.structural_coherence,
            composite_score=score.composite_score,
            seo_score=score.seo_score,
            details=score.details,
            recommendations=score.recommendations
        )
        
    except Exception as e:
        logger.error("content_scoring_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to score content: {str(e)}"
        )


@router.get("/dimensions")
async def get_dimensions():
    """
    Get information about scoring dimensions
    
    Returns details about all 8 scoring dimensions
    """
    return {
        "dimensions": [
            {
                "name": "metadata_alignment",
                "description": "Alignment between metadata (title, description) and content",
                "weight": 0.15,
                "range": "0-100"
            },
            {
                "name": "hierarchical_decomposition",
                "description": "Quality of content organization and logical flow",
                "weight": 0.15,
                "range": "0-100"
            },
            {
                "name": "thematic_unity",
                "description": "Cohesiveness and focus of content themes",
                "weight": 0.20,
                "range": "0-100"
            },
            {
                "name": "balance",
                "description": "Even distribution of topics and sections",
                "weight": 0.10,
                "range": "0-100"
            },
            {
                "name": "query_intent",
                "description": "Alignment with target search query",
                "weight": 0.20,
                "range": "0-100"
            },
            {
                "name": "structural_coherence",
                "description": "Logical flow and progressive development",
                "weight": 0.20,
                "range": "0-100"
            },
            {
                "name": "composite_score",
                "description": "Weighted average of all dimensions",
                "calculation": "weighted_sum",
                "range": "0-100"
            },
            {
                "name": "seo_score",
                "description": "Specialized SEO score combining semantic and traditional factors",
                "calculation": "specialized",
                "range": "0-100"
            }
        ],
        "note": "All scores are on a 0-100 scale where higher is better"
    }

