"""
Embeddings Service - GPU-accelerated semantic analysis
Uses sentence-transformers for generating embeddings from text content
"""
import torch
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from sentence_transformers import SentenceTransformer
import structlog
from functools import lru_cache

from app.core.config import settings

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """
    GPU-accelerated embedding generation service
    Handles batch processing, caching, and semantic similarity computations
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None,
        batch_size: Optional[int] = None
    ):
        """
        Initialize the embedding service
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
            batch_size: Batch size for processing (defaults to config)
        """
        self.model_name = model_name
        self.batch_size = batch_size or settings.GPU_BATCH_SIZE
        
        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        # Load model
        logger.info(
            "initializing_embedding_model",
            model=model_name,
            device=self.device,
            batch_size=self.batch_size
        )
        
        try:
            self.model = SentenceTransformer(model_name)
            self.model.to(self.device)
            
            # Get embedding dimension
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            
            logger.info(
                "embedding_model_loaded",
                model=model_name,
                device=self.device,
                embedding_dim=self.embedding_dim,
                gpu_count=torch.cuda.device_count() if torch.cuda.is_available() else 0
            )
            
        except Exception as e:
            logger.error("failed_to_load_model", model=model_name, error=str(e))
            raise
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: Optional[int] = None,
        show_progress: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            batch_size: Override default batch size
            show_progress: Show progress bar
            normalize: Normalize embeddings to unit length
            
        Returns:
            numpy array of embeddings (n_texts, embedding_dim)
        """
        if isinstance(texts, str):
            texts = [texts]
            
        if len(texts) == 0:
            return np.array([])
        
        batch_size = batch_size or self.batch_size
        
        try:
            logger.debug(
                "generating_embeddings",
                num_texts=len(texts),
                batch_size=batch_size,
                device=self.device
            )
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                device=self.device
            )
            
            logger.debug(
                "embeddings_generated",
                num_embeddings=len(embeddings),
                embedding_shape=embeddings.shape
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(
                "embedding_generation_failed",
                num_texts=len(texts),
                error=str(e)
            )
            raise
    
    def encode_chunks(
        self,
        chunks: List[str],
        metadata: Optional[List[Dict]] = None,
        batch_size: Optional[int] = None
    ) -> List[Dict]:
        """
        Generate embeddings for content chunks with metadata
        
        Args:
            chunks: List of text chunks
            metadata: Optional metadata for each chunk
            batch_size: Override default batch size
            
        Returns:
            List of dicts with 'text', 'embedding', and optional metadata
        """
        if len(chunks) == 0:
            return []
        
        embeddings = self.encode(chunks, batch_size=batch_size)
        
        results = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            result = {
                'text': chunk,
                'embedding': embedding.tolist(),
                'embedding_dim': len(embedding)
            }
            
            # Add metadata if provided
            if metadata and i < len(metadata):
                result['metadata'] = metadata[i]
                
            results.append(result)
            
        return results
    
    def compute_similarity(
        self,
        embedding1: Union[np.ndarray, List[float]],
        embedding2: Union[np.ndarray, List[float]]
    ) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score (0-1, higher is more similar)
        """
        # Convert to numpy if needed
        if isinstance(embedding1, list):
            embedding1 = np.array(embedding1)
        if isinstance(embedding2, list):
            embedding2 = np.array(embedding2)
        
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        
        # Ensure in [0, 1] range (convert from [-1, 1])
        return float((similarity + 1) / 2)
    
    def compute_similarity_matrix(
        self,
        embeddings: Union[List[np.ndarray], np.ndarray]
    ) -> np.ndarray:
        """
        Compute pairwise similarity matrix for a set of embeddings
        
        Args:
            embeddings: Array of embeddings (n_embeddings, embedding_dim)
            
        Returns:
            Similarity matrix (n_embeddings, n_embeddings)
        """
        if isinstance(embeddings, list):
            embeddings = np.array(embeddings)
            
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / norms
        
        # Compute cosine similarity matrix
        similarity_matrix = np.dot(normalized, normalized.T)
        
        # Convert from [-1, 1] to [0, 1]
        return (similarity_matrix + 1) / 2
    
    def find_most_similar(
        self,
        query_embedding: Union[np.ndarray, List[float]],
        candidate_embeddings: List[Union[np.ndarray, List[float]]],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find most similar embeddings to a query
        
        Args:
            query_embedding: Query embedding
            candidate_embeddings: List of candidate embeddings
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        similarities = [
            self.compute_similarity(query_embedding, candidate)
            for candidate in candidate_embeddings
        ]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [(int(idx), float(similarities[idx])) for idx in top_indices]
    
    def compute_centroid(
        self,
        embeddings: Union[List[np.ndarray], np.ndarray]
    ) -> np.ndarray:
        """
        Compute the centroid (mean) of a set of embeddings
        
        Args:
            embeddings: Array of embeddings
            
        Returns:
            Centroid embedding
        """
        if isinstance(embeddings, list):
            embeddings = np.array(embeddings)
            
        return np.mean(embeddings, axis=0)
    
    def semantic_search(
        self,
        query: str,
        corpus: List[str],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Perform semantic search over a corpus
        
        Args:
            query: Search query
            corpus: List of documents to search
            top_k: Number of results to return
            
        Returns:
            List of dicts with 'index', 'text', and 'score'
        """
        # Generate embeddings
        query_embedding = self.encode(query)[0]
        corpus_embeddings = self.encode(corpus)
        
        # Find most similar
        results = self.find_most_similar(
            query_embedding,
            corpus_embeddings,
            top_k=min(top_k, len(corpus))
        )
        
        return [
            {
                'index': idx,
                'text': corpus[idx],
                'score': score
            }
            for idx, score in results
        ]
    
    def cluster_embeddings(
        self,
        embeddings: Union[List[np.ndarray], np.ndarray],
        num_clusters: Optional[int] = None,
        min_cluster_size: int = 5
    ) -> Tuple[np.ndarray, Dict]:
        """
        Cluster embeddings using HDBSCAN
        
        Args:
            embeddings: Array of embeddings
            num_clusters: Target number of clusters (None for auto)
            min_cluster_size: Minimum cluster size for HDBSCAN
            
        Returns:
            Tuple of (cluster_labels, metadata_dict)
        """
        try:
            import hdbscan
        except ImportError:
            logger.error("hdbscan_not_installed")
            raise ImportError("hdbscan is required for clustering")
        
        if isinstance(embeddings, list):
            embeddings = np.array(embeddings)
        
        logger.info(
            "clustering_embeddings",
            num_embeddings=len(embeddings),
            min_cluster_size=min_cluster_size
        )
        
        # Perform clustering
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        
        labels = clusterer.fit_predict(embeddings)
        
        # Compute metadata
        unique_labels = np.unique(labels)
        num_clusters = len(unique_labels[unique_labels >= 0])  # Exclude noise (-1)
        num_noise = np.sum(labels == -1)
        
        metadata = {
            'num_clusters': num_clusters,
            'num_noise_points': num_noise,
            'cluster_sizes': {
                int(label): int(np.sum(labels == label))
                for label in unique_labels
            },
            'cluster_persistence': clusterer.cluster_persistence_.tolist()
            if hasattr(clusterer, 'cluster_persistence_') else None
        }
        
        logger.info(
            "clustering_complete",
            num_clusters=num_clusters,
            num_noise=num_noise
        )
        
        return labels, metadata
    
    def get_device_info(self) -> Dict:
        """Get information about the device being used"""
        info = {
            'device': self.device,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim,
            'batch_size': self.batch_size
        }
        
        if torch.cuda.is_available():
            info.update({
                'cuda_available': True,
                'gpu_count': torch.cuda.device_count(),
                'gpu_devices': [
                    {
                        'name': torch.cuda.get_device_name(i),
                        'memory_total': torch.cuda.get_device_properties(i).total_memory,
                        'memory_allocated': torch.cuda.memory_allocated(i),
                        'memory_reserved': torch.cuda.memory_reserved(i)
                    }
                    for i in range(torch.cuda.device_count())
                ]
            })
        else:
            info['cuda_available'] = False
            
        return info


# Singleton instance with caching
@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """
    Get or create singleton embedding service instance
    Uses LRU cache to ensure single instance
    """
    return EmbeddingService()

