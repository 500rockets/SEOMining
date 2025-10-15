"""
Embedding services for SEO Mining.

Provides local GPU-accelerated embeddings using sentence-transformers
with fallback to OpenAI API if needed.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

__all__ = ['get_embedding_service', 'EmbeddingService']


class EmbeddingService:
    """Base interface for embedding services."""
    
    async def embed_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Optional batch size override
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        raise NotImplementedError


def get_embedding_service(use_gpu: bool = True) -> EmbeddingService:
    """
    Factory function to get the appropriate embedding service.
    
    Args:
        use_gpu: If True, use local GPU. If False, use OpenAI API.
        
    Returns:
        EmbeddingService instance
    """
    # TODO: Implement in Phase 2
    # if use_gpu:
    #     from .local_gpu_embedder import LocalGPUEmbedder
    #     return LocalGPUEmbedder()
    # else:
    #     from .openai_embedder import OpenAIEmbedder
    #     return OpenAIEmbedder()
    
    logger.warning("Embedding service not yet implemented (Phase 2)")
    return None

