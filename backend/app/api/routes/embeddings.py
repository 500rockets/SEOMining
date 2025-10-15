"""
API endpoints for Embeddings Service
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import structlog

from app.services.embeddings import get_embedding_service, chunk_for_embeddings

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/embeddings", tags=["embeddings"])


# Request/Response Models
class EmbedTextRequest(BaseModel):
    """Request model for text embedding"""
    text: str = Field(..., description="Text to embed")
    normalize: bool = Field(True, description="Normalize embeddings to unit length")


class EmbedBatchRequest(BaseModel):
    """Request model for batch embedding"""
    texts: List[str] = Field(..., description="List of texts to embed")
    normalize: bool = Field(True, description="Normalize embeddings to unit length")
    batch_size: Optional[int] = Field(None, description="Override default batch size")


class EmbeddingResponse(BaseModel):
    """Response model for single embedding"""
    embedding: List[float]
    dimension: int
    text_length: int


class BatchEmbeddingResponse(BaseModel):
    """Response model for batch embeddings"""
    embeddings: List[List[float]]
    dimension: int
    count: int


class SimilarityRequest(BaseModel):
    """Request model for similarity computation"""
    embedding1: List[float]
    embedding2: List[float]


class SimilarityResponse(BaseModel):
    """Response model for similarity"""
    similarity: float
    description: str


class SemanticSearchRequest(BaseModel):
    """Request model for semantic search"""
    query: str = Field(..., description="Search query")
    corpus: List[str] = Field(..., description="Documents to search")
    top_k: int = Field(5, ge=1, le=100, description="Number of results to return")


class SearchResult(BaseModel):
    """Single search result"""
    index: int
    text: str
    score: float


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search"""
    query: str
    results: List[SearchResult]
    total_searched: int


class ChunkRequest(BaseModel):
    """Request model for text chunking"""
    text: str = Field(..., description="Text to chunk")
    chunk_size: int = Field(512, ge=50, le=2048, description="Target chunk size")
    overlap: int = Field(50, ge=0, le=500, description="Overlap between chunks")
    preserve_structure: bool = Field(True, description="Respect paragraph boundaries")


class ChunkResponse(BaseModel):
    """Response model for chunking"""
    chunks: List[str]
    count: int
    avg_chunk_size: int


class DeviceInfoResponse(BaseModel):
    """Response model for device information"""
    device: str
    model_name: str
    embedding_dim: int
    batch_size: int
    cuda_available: bool
    gpu_count: Optional[int] = None
    gpu_devices: Optional[List[Dict[str, Any]]] = None


# Endpoints
@router.post("/embed", response_model=EmbeddingResponse)
async def embed_text(request: EmbedTextRequest):
    """
    Generate embedding for a single text
    
    Returns a high-dimensional vector representation of the input text
    """
    try:
        service = get_embedding_service()
        embedding = service.encode(request.text, normalize=request.normalize)
        
        return EmbeddingResponse(
            embedding=embedding[0].tolist(),
            dimension=len(embedding[0]),
            text_length=len(request.text)
        )
        
    except Exception as e:
        logger.error("embed_text_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {str(e)}"
        )


@router.post("/embed/batch", response_model=BatchEmbeddingResponse)
async def embed_batch(request: EmbedBatchRequest):
    """
    Generate embeddings for multiple texts in batch
    
    More efficient than calling /embed multiple times
    """
    try:
        service = get_embedding_service()
        embeddings = service.encode(
            request.texts,
            normalize=request.normalize,
            batch_size=request.batch_size
        )
        
        return BatchEmbeddingResponse(
            embeddings=[emb.tolist() for emb in embeddings],
            dimension=len(embeddings[0]),
            count=len(embeddings)
        )
        
    except Exception as e:
        logger.error("embed_batch_failed", error=str(e), num_texts=len(request.texts))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings: {str(e)}"
        )


@router.post("/similarity", response_model=SimilarityResponse)
async def compute_similarity(request: SimilarityRequest):
    """
    Compute cosine similarity between two embeddings
    
    Returns a score between 0 (completely different) and 1 (identical)
    """
    try:
        service = get_embedding_service()
        similarity = service.compute_similarity(
            request.embedding1,
            request.embedding2
        )
        
        # Provide human-readable description
        if similarity > 0.9:
            description = "Very similar"
        elif similarity > 0.7:
            description = "Similar"
        elif similarity > 0.5:
            description = "Somewhat similar"
        elif similarity > 0.3:
            description = "Slightly similar"
        else:
            description = "Different"
        
        return SimilarityResponse(
            similarity=similarity,
            description=description
        )
        
    except Exception as e:
        logger.error("compute_similarity_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute similarity: {str(e)}"
        )


@router.post("/search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """
    Perform semantic search over a corpus of documents
    
    Finds documents most semantically similar to the query
    """
    try:
        service = get_embedding_service()
        results = service.semantic_search(
            request.query,
            request.corpus,
            top_k=request.top_k
        )
        
        return SemanticSearchResponse(
            query=request.query,
            results=[SearchResult(**r) for r in results],
            total_searched=len(request.corpus)
        )
        
    except Exception as e:
        logger.error("semantic_search_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/chunk", response_model=ChunkResponse)
async def chunk_text(request: ChunkRequest):
    """
    Split text into semantic chunks for embedding generation
    
    Useful for processing long documents
    """
    try:
        chunks = chunk_for_embeddings(
            request.text,
            chunk_size=request.chunk_size,
            overlap=request.overlap,
            preserve_structure=request.preserve_structure
        )
        
        avg_size = sum(len(c) for c in chunks) // len(chunks) if chunks else 0
        
        return ChunkResponse(
            chunks=chunks,
            count=len(chunks),
            avg_chunk_size=avg_size
        )
        
    except Exception as e:
        logger.error("chunk_text_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to chunk text: {str(e)}"
        )


@router.get("/device-info", response_model=DeviceInfoResponse)
async def get_device_info():
    """
    Get information about the embedding service device (GPU/CPU)
    
    Useful for debugging and performance monitoring
    """
    try:
        service = get_embedding_service()
        info = service.get_device_info()
        
        return DeviceInfoResponse(**info)
        
    except Exception as e:
        logger.error("get_device_info_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device info: {str(e)}"
        )


@router.get("/models")
async def list_available_models():
    """
    List commonly used sentence-transformer models
    
    Note: Changing models requires rebuilding the service
    """
    return {
        "current_model": "all-MiniLM-L6-v2",
        "available_models": [
            {
                "name": "all-MiniLM-L6-v2",
                "dimension": 384,
                "description": "Fast and efficient, good for most tasks",
                "performance": "Fast",
                "quality": "Good"
            },
            {
                "name": "all-mpnet-base-v2",
                "dimension": 768,
                "description": "Higher quality embeddings, slower",
                "performance": "Medium",
                "quality": "Excellent"
            },
            {
                "name": "multi-qa-MiniLM-L6-cos-v1",
                "dimension": 384,
                "description": "Optimized for semantic search and Q&A",
                "performance": "Fast",
                "quality": "Good"
            },
            {
                "name": "paraphrase-multilingual-MiniLM-L12-v2",
                "dimension": 384,
                "description": "Supports 50+ languages",
                "performance": "Medium",
                "quality": "Good"
            }
        ],
        "note": "Model changes require service restart"
    }

