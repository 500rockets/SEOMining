"""
Scoring Service - 8-Dimensional Content Analysis
Uses embeddings for semantic scoring and structural analysis
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import structlog

from app.services.embeddings import get_embedding_service

logger = structlog.get_logger(__name__)


@dataclass
class ContentScore:
    """Complete content scoring result"""
    # Individual dimension scores (0-100)
    metadata_alignment: float
    hierarchical_decomposition: float
    thematic_unity: float
    balance: float
    query_intent: float
    structural_coherence: float
    
    # Aggregate scores
    composite_score: float
    seo_score: float
    
    # Supporting data
    details: Dict
    recommendations: List[str]


class ScoringService:
    """
    8-Dimensional Content Scoring Service
    Analyzes content quality, structure, and SEO potential
    """
    
    def __init__(self):
        """Initialize scoring service"""
        self.embedding_service = get_embedding_service()
        
        # Dimension weights for composite score
        self.weights = {
            'metadata_alignment': 0.15,
            'hierarchical_decomposition': 0.15,
            'thematic_unity': 0.20,
            'balance': 0.10,
            'query_intent': 0.20,
            'structural_coherence': 0.20
        }
    
    def score_content(
        self,
        content: Dict,
        query: Optional[str] = None,
        competitor_contents: Optional[List[Dict]] = None
    ) -> ContentScore:
        """
        Generate complete 8-dimensional score for content
        
        Args:
            content: Content dict with 'text', 'title', 'description', etc.
            query: Target search query (optional)
            competitor_contents: List of competitor content dicts (optional)
            
        Returns:
            ContentScore with all dimensions
        """
        logger.info(
            "scoring_content",
            has_query=bool(query),
            has_competitors=bool(competitor_contents)
        )
        
        # Extract text and metadata
        text = content.get('text', '')
        title = content.get('title', '')
        description = content.get('description', '')
        
        # Generate chunks and embeddings
        from app.services.embeddings import chunk_for_embeddings
        chunks = chunk_for_embeddings(text, chunk_size=512, overlap=50)
        
        if not chunks:
            logger.warning("no_chunks_generated")
            return self._create_zero_score("No content to analyze")
        
        chunk_embeddings = self.embedding_service.encode(chunks)
        
        # Score each dimension
        scores = {}
        details = {}
        
        # 1. Metadata Alignment
        scores['metadata_alignment'], details['metadata'] = self._score_metadata_alignment(
            title, description, text, chunk_embeddings
        )
        
        # 2. Hierarchical Decomposition
        scores['hierarchical_decomposition'], details['hierarchy'] = self._score_hierarchical_decomposition(
            chunks, chunk_embeddings
        )
        
        # 3. Thematic Unity
        scores['thematic_unity'], details['thematic'] = self._score_thematic_unity(
            chunk_embeddings
        )
        
        # 4. Balance
        scores['balance'], details['balance'] = self._score_balance(
            chunks, chunk_embeddings
        )
        
        # 5. Query Intent (if query provided)
        if query:
            scores['query_intent'], details['query'] = self._score_query_intent(
                query, text, chunk_embeddings
            )
        else:
            scores['query_intent'] = 50.0  # Neutral score
            details['query'] = {'note': 'No query provided'}
        
        # 6. Structural Coherence
        scores['structural_coherence'], details['structure'] = self._score_structural_coherence(
            chunks, chunk_embeddings
        )
        
        # 7. Composite Score (weighted average)
        composite = sum(
            scores[dim] * self.weights[dim]
            for dim in self.weights.keys()
        )
        
        # 8. SEO Score (specialized calculation)
        seo_score = self._calculate_seo_score(scores, title, description, text)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scores, details)
        
        return ContentScore(
            metadata_alignment=scores['metadata_alignment'],
            hierarchical_decomposition=scores['hierarchical_decomposition'],
            thematic_unity=scores['thematic_unity'],
            balance=scores['balance'],
            query_intent=scores['query_intent'],
            structural_coherence=scores['structural_coherence'],
            composite_score=composite,
            seo_score=seo_score,
            details=details,
            recommendations=recommendations
        )
    
    def _score_metadata_alignment(
        self,
        title: str,
        description: str,
        text: str,
        chunk_embeddings: np.ndarray
    ) -> Tuple[float, Dict]:
        """
        Score alignment between metadata (title, description) and content
        
        Returns:
            Tuple of (score 0-100, details dict)
        """
        try:
            # Embed metadata
            metadata_texts = [t for t in [title, description] if t]
            if not metadata_texts:
                return 0.0, {'error': 'No metadata available'}
            
            metadata_embeddings = self.embedding_service.encode(metadata_texts)
            
            # Compute centroid of content chunks
            content_centroid = self.embedding_service.compute_centroid(chunk_embeddings)
            
            # Compare metadata to content centroid
            similarities = [
                self.embedding_service.compute_similarity(meta_emb, content_centroid)
                for meta_emb in metadata_embeddings
            ]
            
            avg_similarity = np.mean(similarities)
            score = avg_similarity * 100
            
            details = {
                'title_alignment': similarities[0] if title else None,
                'description_alignment': similarities[1] if description and len(similarities) > 1 else None,
                'average_similarity': avg_similarity
            }
            
            logger.debug("metadata_alignment_scored", score=score)
            return score, details
            
        except Exception as e:
            logger.error("metadata_scoring_failed", error=str(e))
            return 0.0, {'error': str(e)}
    
    def _score_hierarchical_decomposition(
        self,
        chunks: List[str],
        chunk_embeddings: np.ndarray
    ) -> Tuple[float, Dict]:
        """
        Score how well content is organized hierarchically
        Measures progression and logical flow
        
        Returns:
            Tuple of (score 0-100, details dict)
        """
        try:
            if len(chunks) < 2:
                return 50.0, {'note': 'Insufficient chunks for hierarchy analysis'}
            
            # Compute sequential similarities (chunk N to chunk N+1)
            sequential_sims = []
            for i in range(len(chunk_embeddings) - 1):
                sim = self.embedding_service.compute_similarity(
                    chunk_embeddings[i],
                    chunk_embeddings[i + 1]
                )
                sequential_sims.append(sim)
            
            # Good hierarchy has moderate sequential similarity
            # (not too similar = repetitive, not too different = disjointed)
            avg_seq_sim = np.mean(sequential_sims)
            std_seq_sim = np.std(sequential_sims)
            
            # Optimal range: 0.5-0.7 similarity with low variance
            optimal_sim = 0.6
            sim_distance = abs(avg_seq_sim - optimal_sim)
            
            # Score based on distance from optimal and consistency
            sim_score = max(0, 1 - (sim_distance / 0.3)) * 100
            consistency_score = max(0, 1 - (std_seq_sim / 0.2)) * 100
            
            score = (sim_score * 0.6 + consistency_score * 0.4)
            
            details = {
                'avg_sequential_similarity': avg_seq_sim,
                'similarity_std': std_seq_sim,
                'progression_quality': 'good' if avg_seq_sim > 0.5 else 'needs improvement',
                'consistency': 'high' if std_seq_sim < 0.15 else 'low'
            }
            
            logger.debug("hierarchical_decomposition_scored", score=score)
            return score, details
            
        except Exception as e:
            logger.error("hierarchy_scoring_failed", error=str(e))
            return 0.0, {'error': str(e)}
    
    def _score_thematic_unity(
        self,
        chunk_embeddings: np.ndarray
    ) -> Tuple[float, Dict]:
        """
        Score thematic unity - how cohesive the content is
        Higher average similarity = more unified theme
        
        Returns:
            Tuple of (score 0-100, details dict)
        """
        try:
            if len(chunk_embeddings) < 2:
                return 50.0, {'note': 'Insufficient chunks for unity analysis'}
            
            # Compute pairwise similarity matrix
            similarity_matrix = self.embedding_service.compute_similarity_matrix(chunk_embeddings)
            
            # Average similarity (excluding diagonal)
            mask = ~np.eye(len(chunk_embeddings), dtype=bool)
            avg_similarity = similarity_matrix[mask].mean()
            
            # Convert to 0-100 scale
            score = avg_similarity * 100
            
            # Identify outlier chunks (low similarity to others)
            chunk_avg_sims = similarity_matrix.mean(axis=1)
            outlier_threshold = avg_similarity - (1.5 * chunk_avg_sims.std())
            outliers = np.where(chunk_avg_sims < outlier_threshold)[0]
            
            details = {
                'average_similarity': avg_similarity,
                'similarity_std': chunk_avg_sims.std(),
                'outlier_chunks': outliers.tolist(),
                'cohesiveness': 'high' if avg_similarity > 0.7 else 'moderate' if avg_similarity > 0.5 else 'low'
            }
            
            logger.debug("thematic_unity_scored", score=score)
            return score, details
            
        except Exception as e:
            logger.error("thematic_unity_scoring_failed", error=str(e))
            return 0.0, {'error': str(e)}
    
    def _score_balance(
        self,
        chunks: List[str],
        chunk_embeddings: np.ndarray
    ) -> Tuple[float, Dict]:
        """
        Score content balance - even distribution of topics/sections
        
        Returns:
            Tuple of (score 0-100, details dict)
        """
        try:
            if len(chunks) < 3:
                return 50.0, {'note': 'Insufficient chunks for balance analysis'}
            
            # Analyze chunk size variance
            chunk_sizes = [len(chunk) for chunk in chunks]
            avg_size = np.mean(chunk_sizes)
            size_std = np.std(chunk_sizes)
            size_cv = size_std / avg_size if avg_size > 0 else 1.0  # Coefficient of variation
            
            # Score based on size consistency (lower CV = better balance)
            size_score = max(0, 1 - size_cv) * 100
            
            # Semantic diversity - measure coverage of semantic space
            chunk_avg_sims = self.embedding_service.compute_similarity_matrix(chunk_embeddings).mean(axis=1)
            diversity_score = (1 - chunk_avg_sims.std()) * 100
            
            # Combined score
            score = (size_score * 0.4 + diversity_score * 0.6)
            
            details = {
                'avg_chunk_size': avg_size,
                'size_std': size_std,
                'size_coefficient_variation': size_cv,
                'semantic_diversity': diversity_score,
                'balance_quality': 'good' if score > 70 else 'needs improvement'
            }
            
            logger.debug("balance_scored", score=score)
            return score, details
            
        except Exception as e:
            logger.error("balance_scoring_failed", error=str(e))
            return 0.0, {'error': str(e)}
    
    def _score_query_intent(
        self,
        query: str,
        text: str,
        chunk_embeddings: np.ndarray
    ) -> Tuple[float, Dict]:
        """
        Score how well content matches query intent
        
        Returns:
            Tuple of (score 0-100, details dict)
        """
        try:
            # Embed query
            query_embedding = self.embedding_service.encode(query)[0]
            
            # Compute similarity to all chunks
            chunk_similarities = [
                self.embedding_service.compute_similarity(query_embedding, chunk_emb)
                for chunk_emb in chunk_embeddings
            ]
            
            # Overall query alignment
            avg_similarity = np.mean(chunk_similarities)
            max_similarity = np.max(chunk_similarities)
            
            # Score based on average and max alignment
            score = (avg_similarity * 0.6 + max_similarity * 0.4) * 100
            
            # Find best matching chunks
            top_indices = np.argsort(chunk_similarities)[-3:][::-1]
            
            details = {
                'average_alignment': avg_similarity,
                'max_alignment': max_similarity,
                'top_matching_chunks': top_indices.tolist(),
                'query': query,
                'alignment_quality': 'excellent' if avg_similarity > 0.7 else 'good' if avg_similarity > 0.5 else 'needs improvement'
            }
            
            logger.debug("query_intent_scored", score=score, query=query)
            return score, details
            
        except Exception as e:
            logger.error("query_intent_scoring_failed", error=str(e))
            return 0.0, {'error': str(e)}
    
    def _score_structural_coherence(
        self,
        chunks: List[str],
        chunk_embeddings: np.ndarray
    ) -> Tuple[float, Dict]:
        """
        Score structural coherence - logical flow and organization
        Combines multiple structural metrics
        
        Returns:
            Tuple of (score 0-100, details dict)
        """
        try:
            if len(chunks) < 3:
                return 50.0, {'note': 'Insufficient chunks for structure analysis'}
            
            # 1. Flow consistency (adjacent chunks should be related)
            flow_scores = []
            for i in range(len(chunk_embeddings) - 1):
                sim = self.embedding_service.compute_similarity(
                    chunk_embeddings[i],
                    chunk_embeddings[i + 1]
                )
                flow_scores.append(sim)
            
            avg_flow = np.mean(flow_scores)
            flow_consistency = 1 - np.std(flow_scores)
            
            # 2. Progressive development (gradual topic evolution)
            # Measure how similarity decreases with distance
            distance_sims = []
            for distance in range(1, min(5, len(chunks))):
                sims = []
                for i in range(len(chunk_embeddings) - distance):
                    sim = self.embedding_service.compute_similarity(
                        chunk_embeddings[i],
                        chunk_embeddings[i + distance]
                    )
                    sims.append(sim)
                if sims:
                    distance_sims.append(np.mean(sims))
            
            # Good structure shows gradual decrease in similarity
            if len(distance_sims) > 1:
                progression = -np.mean(np.diff(distance_sims))  # Negative diff = decrease
                progression_score = min(100, max(0, progression * 200))
            else:
                progression_score = 50.0
            
            # Combined structural score
            score = (
                avg_flow * 40 +
                flow_consistency * 30 +
                progression_score * 0.3
            )
            
            details = {
                'average_flow': avg_flow,
                'flow_consistency': flow_consistency,
                'progression_score': progression_score,
                'structural_quality': 'excellent' if score > 75 else 'good' if score > 60 else 'needs improvement'
            }
            
            logger.debug("structural_coherence_scored", score=score)
            return score, details
            
        except Exception as e:
            logger.error("structural_coherence_scoring_failed", error=str(e))
            return 0.0, {'error': str(e)}
    
    def _calculate_seo_score(
        self,
        dimension_scores: Dict[str, float],
        title: str,
        description: str,
        text: str
    ) -> float:
        """
        Calculate specialized SEO score
        Combines semantic scores with traditional SEO factors
        
        Returns:
            SEO score (0-100)
        """
        # Start with composite of key dimensions
        semantic_score = (
            dimension_scores['metadata_alignment'] * 0.25 +
            dimension_scores['thematic_unity'] * 0.25 +
            dimension_scores['query_intent'] * 0.30 +
            dimension_scores['structural_coherence'] * 0.20
        )
        
        # Traditional SEO factors
        has_title = bool(title and len(title) > 0)
        has_description = bool(description and len(description) > 0)
        good_length = 300 <= len(text) <= 5000
        
        traditional_bonus = 0
        if has_title:
            traditional_bonus += 5
        if has_description:
            traditional_bonus += 5
        if good_length:
            traditional_bonus += 5
        
        seo_score = min(100, semantic_score + traditional_bonus)
        
        logger.debug("seo_score_calculated", score=seo_score)
        return seo_score
    
    def _generate_recommendations(
        self,
        scores: Dict[str, float],
        details: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on scores"""
        recommendations = []
        
        # Metadata alignment
        if scores['metadata_alignment'] < 70:
            recommendations.append(
                "Improve metadata alignment: Ensure title and description accurately reflect main content themes"
            )
        
        # Hierarchical decomposition
        if scores['hierarchical_decomposition'] < 65:
            recommendations.append(
                "Enhance content structure: Use clear headings and logical progression between sections"
            )
        
        # Thematic unity
        if scores['thematic_unity'] < 60:
            recommendations.append(
                "Strengthen thematic unity: Remove off-topic content and maintain focus on core themes"
            )
        
        # Balance
        if scores['balance'] < 65:
            recommendations.append(
                "Improve content balance: Distribute content more evenly across sections"
            )
        
        # Query intent
        if scores['query_intent'] < 70:
            recommendations.append(
                "Better target query intent: Include more content directly addressing the search query"
            )
        
        # Structural coherence
        if scores['structural_coherence'] < 65:
            recommendations.append(
                "Enhance structural coherence: Improve logical flow and transitions between sections"
            )
        
        # If all scores are good
        if all(score > 75 for score in scores.values()):
            recommendations.append(
                "Excellent content! Maintain current quality and continue optimizing for target keywords"
            )
        
        return recommendations
    
    def _create_zero_score(self, reason: str) -> ContentScore:
        """Create a zero score with error message"""
        return ContentScore(
            metadata_alignment=0.0,
            hierarchical_decomposition=0.0,
            thematic_unity=0.0,
            balance=0.0,
            query_intent=0.0,
            structural_coherence=0.0,
            composite_score=0.0,
            seo_score=0.0,
            details={'error': reason},
            recommendations=[f"Error: {reason}"]
        )


# Singleton instance
_scoring_service_instance = None


def get_scoring_service() -> ScoringService:
    """Get or create singleton scoring service instance"""
    global _scoring_service_instance
    
    if _scoring_service_instance is None:
        _scoring_service_instance = ScoringService()
    
    return _scoring_service_instance

