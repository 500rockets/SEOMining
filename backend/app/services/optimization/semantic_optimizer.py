"""
Semantic Optimization Service
GPU-accelerated phrase/keyword analysis for score optimization
"""
import numpy as np
from typing import List, Dict, Tuple, Set
from collections import Counter
import re
from scipy.spatial.distance import cosine
import structlog

from app.services.embeddings import EmbeddingService

logger = structlog.get_logger(__name__)


class SemanticOptimizer:
    """
    Analyzes semantic gaps between target content and top performers
    Identifies specific phrases/concepts that would improve scores
    """
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        
    async def analyze_semantic_gaps(
        self,
        target_content: str,
        competitor_contents: List[str],
        query: str,
        top_n_phrases: int = 50
    ) -> Dict:
        """
        Deep semantic analysis to find specific improvements
        
        Args:
            target_content: Your content
            competitor_contents: List of competitor content strings
            query: Target search query
            top_n_phrases: Number of phrase recommendations to return
            
        Returns:
            Dict with recommendations and impact estimates
        """
        logger.info(
            "semantic_gap_analysis_starting",
            target_length=len(target_content),
            competitor_count=len(competitor_contents),
            query=query
        )
        
        # Extract phrases from all content
        target_phrases = self._extract_phrases(target_content)
        competitor_phrases_list = [
            self._extract_phrases(content) 
            for content in competitor_contents
        ]
        
        # Find common competitor phrases (present in multiple competitors)
        all_competitor_phrases = []
        for phrases in competitor_phrases_list:
            all_competitor_phrases.extend(phrases)
        
        phrase_frequency = Counter(all_competitor_phrases)
        
        # Phrases appearing in 3+ competitors are significant
        significant_competitor_phrases = {
            phrase: count 
            for phrase, count in phrase_frequency.items() 
            if count >= 3
        }
        
        # Find missing phrases (in competitors but not in target)
        target_phrase_set = set(target_phrases)
        missing_phrases = [
            phrase for phrase in significant_competitor_phrases.keys()
            if phrase not in target_phrase_set
        ]
        
        logger.info(
            "phrases_extracted",
            target_phrases=len(target_phrases),
            competitor_phrases=len(all_competitor_phrases),
            significant_phrases=len(significant_competitor_phrases),
            missing_phrases=len(missing_phrases)
        )
        
        # Analyze semantic relevance of missing phrases
        if missing_phrases:
            phrase_analysis = await self._analyze_phrase_relevance(
                missing_phrases,
                query,
                target_content,
                competitor_contents
            )
        else:
            phrase_analysis = []
        
        # Sort by potential impact
        phrase_analysis.sort(key=lambda x: x['estimated_impact'], reverse=True)
        
        return {
            'missing_concepts': phrase_analysis[:top_n_phrases],
            'coverage_stats': {
                'your_unique_phrases': len(target_phrase_set),
                'competitor_common_phrases': len(significant_competitor_phrases),
                'semantic_gaps_found': len(missing_phrases),
                'high_impact_recommendations': len([p for p in phrase_analysis if p['estimated_impact'] > 5.0])
            }
        }
    
    async def _analyze_phrase_relevance(
        self,
        phrases: List[str],
        query: str,
        target_content: str,
        competitor_contents: List[str]
    ) -> List[Dict]:
        """
        Analyze each missing phrase for semantic relevance and impact
        """
        # Generate embeddings for all phrases + query
        texts_to_embed = [query] + phrases
        embeddings = self.embedding_service.encode(texts_to_embed)
        
        query_embedding = embeddings[0]
        phrase_embeddings = embeddings[1:]
        
        # Analyze each phrase
        results = []
        for phrase, phrase_emb in zip(phrases, phrase_embeddings):
            # Calculate query relevance
            query_similarity = 1 - cosine(phrase_emb, query_embedding)
            
            # Calculate how many competitors use this phrase
            competitor_usage = sum(
                1 for content in competitor_contents 
                if phrase.lower() in content.lower()
            )
            
            # Estimate impact based on:
            # 1. Query relevance (how related to search query)
            # 2. Competitor adoption (how many top performers use it)
            # 3. Phrase importance (length/specificity)
            
            query_impact = query_similarity * 10  # Max 10 points
            adoption_impact = (competitor_usage / len(competitor_contents)) * 5  # Max 5 points
            
            estimated_impact = query_impact + adoption_impact
            
            results.append({
                'phrase': phrase,
                'estimated_impact': round(estimated_impact, 2),
                'query_relevance': round(query_similarity * 100, 1),
                'competitor_usage': competitor_usage,
                'competitor_usage_pct': round((competitor_usage / len(competitor_contents)) * 100, 1),
                'recommendation': self._generate_recommendation(phrase, estimated_impact)
            })
        
        return results
    
    def _extract_phrases(
        self,
        content: str,
        min_length: int = 15,
        max_length: int = 100
    ) -> List[str]:
        """
        Extract meaningful phrases from content
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        phrases = []
        for sentence in sentences:
            sentence = sentence.strip()
            if min_length <= len(sentence) <= max_length:
                # Clean up
                sentence = re.sub(r'\s+', ' ', sentence)
                if len(sentence.split()) >= 3:  # At least 3 words
                    phrases.append(sentence)
        
        # Also extract common n-grams (2-5 words)
        words = content.lower().split()
        for n in range(2, 6):  # 2 to 5 word phrases
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                # Filter out common stop phrases
                if not self._is_stop_phrase(phrase):
                    phrases.append(phrase)
        
        return phrases
    
    def _is_stop_phrase(self, phrase: str) -> bool:
        """Filter out common stop phrases"""
        stop_patterns = [
            r'^the\s',
            r'^a\s',
            r'^an\s',
            r'^and\s',
            r'^or\s',
            r'^but\s',
            r'^in\s',
            r'^on\s',
            r'^at\s',
            r'^to\s',
            r'^for\s'
        ]
        for pattern in stop_patterns:
            if re.match(pattern, phrase):
                return True
        return False
    
    def _generate_recommendation(self, phrase: str, impact: float) -> str:
        """Generate actionable recommendation"""
        if impact > 10:
            return f"HIGH PRIORITY: Add this concept to your content for significant impact"
        elif impact > 5:
            return f"MEDIUM PRIORITY: Including this would improve relevance"
        else:
            return f"LOW PRIORITY: Minor improvement potential"
    
    async def optimize_for_dimension(
        self,
        target_content: str,
        dimension: str,
        top_performers: List[str],
        query: str
    ) -> Dict:
        """
        Optimize content for a specific scoring dimension
        """
        dimension_strategies = {
            'query_intent': await self._optimize_query_intent(
                target_content, top_performers, query
            ),
            'metadata_alignment': await self._optimize_metadata(
                target_content, top_performers, query
            ),
            'thematic_unity': await self._optimize_thematic_unity(
                target_content, top_performers
            ),
            'structural_coherence': await self._optimize_structure(
                target_content, top_performers
            )
        }
        
        return dimension_strategies.get(
            dimension,
            {'error': f'No optimization strategy for dimension: {dimension}'}
        )
    
    async def _optimize_query_intent(
        self,
        target: str,
        performers: List[str],
        query: str
    ) -> Dict:
        """
        Specific optimizations for query intent dimension
        """
        # Find phrases in top performers that directly address the query
        query_embedding = self.embedding_service.encode([query])[0]
        
        recommendations = []
        
        # Extract phrases from top performers
        for performer in performers:
            phrases = self._extract_phrases(performer, min_length=20, max_length=80)
            
            # Find most query-relevant phrases
            if phrases:
                phrase_embeddings = self.embedding_service.encode(phrases[:50])  # Limit for speed
                
                for phrase, emb in zip(phrases[:50], phrase_embeddings):
                    similarity = 1 - cosine(emb, query_embedding)
                    if similarity > 0.7 and phrase.lower() not in target.lower():  # High relevance
                        recommendations.append({
                            'phrase': phrase,
                            'query_match': round(similarity * 100, 1),
                            'type': 'direct_answer'
                        })
        
        # Sort by relevance
        recommendations.sort(key=lambda x: x['query_match'], reverse=True)
        
        return {
            'dimension': 'query_intent',
            'strategy': 'Add phrases that directly answer the search query',
            'recommendations': recommendations[:10],
            'expected_improvement': '5-8 points' if recommendations else '0-2 points'
        }
    
    async def _optimize_metadata(
        self,
        target: str,
        performers: List[str],
        query: str
    ) -> Dict:
        """
        Optimize metadata alignment
        """
        # Analyze what makes top performer metadata effective
        # This would typically analyze titles/descriptions from scraped data
        
        return {
            'dimension': 'metadata_alignment',
            'strategy': 'Align title and description with main content themes',
            'recommendations': [
                {
                    'element': 'title',
                    'suggestion': f'Include "{query}" and main content topics',
                    'example': 'Update title to reflect core services listed on page'
                },
                {
                    'element': 'description',
                    'suggestion': 'Mirror the opening paragraph themes',
                    'example': 'Description should match first 2-3 content sections'
                }
            ],
            'expected_improvement': '6-10 points'
        }
    
    async def _optimize_thematic_unity(
        self,
        target: str,
        performers: List[str]
    ) -> Dict:
        """
        Improve thematic focus
        """
        return {
            'dimension': 'thematic_unity',
            'strategy': 'Remove off-topic content and strengthen core themes',
            'recommendations': [
                {
                    'action': 'audit_content',
                    'description': 'Identify sections that drift from main topic',
                    'method': 'Review each section\'s relevance to core theme'
                },
                {
                    'action': 'strengthen_connections',
                    'description': 'Add connecting phrases between sections',
                    'method': 'Use transition sentences that reference previous section'
                }
            ],
            'expected_improvement': '2-4 points'
        }
    
    async def _optimize_structure(
        self,
        target: str,
        performers: List[str]
    ) -> Dict:
        """
        Improve structural coherence
        """
        return {
            'dimension': 'structural_coherence',
            'strategy': 'Improve logical flow and section transitions',
            'recommendations': [
                {
                    'action': 'add_transitions',
                    'description': 'Connect adjacent sections with transitional phrases',
                    'examples': [
                        'Now that we\'ve covered X, let\'s explore Y...',
                        'Building on this foundation...',
                        'This leads us to...'
                    ]
                },
                {
                    'action': 'progressive_disclosure',
                    'description': 'Arrange content from general to specific',
                    'method': 'Start with overview, then drill into details'
                }
            ],
            'expected_improvement': '4-7 points'
        }


async def get_semantic_optimizer() -> SemanticOptimizer:
    """Factory function to create SemanticOptimizer with dependencies"""
    from app.services.embeddings import get_embedding_service
    embedding_service = get_embedding_service()
    return SemanticOptimizer(embedding_service)

