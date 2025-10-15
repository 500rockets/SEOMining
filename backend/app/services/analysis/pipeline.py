"""
Analysis Pipeline - End-to-End SEO Analysis Workflow
SERP → Scrape → Chunk → Embed → Score → Insights
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import structlog

from app.services.serp import get_serp_service
from app.services.scraping import get_scraping_service
from app.services.embeddings import get_embedding_service, chunk_for_embeddings
from app.services.scoring import get_scoring_service, ContentScore

logger = structlog.get_logger(__name__)


@dataclass
class CompetitorAnalysis:
    """Single competitor analysis result"""
    position: int
    url: str
    title: str
    score: ContentScore
    content_length: int
    chunk_count: int


@dataclass
class AnalysisPipelineResult:
    """Complete pipeline analysis result"""
    query: str
    target_url: Optional[str]
    target_score: Optional[ContentScore]
    competitors: List[CompetitorAnalysis]
    insights: Dict
    recommendations: List[str]


class AnalysisPipeline:
    """
    End-to-end SEO analysis pipeline
    Orchestrates all services for complete competitive analysis
    """
    
    def __init__(
        self,
        serp_api_key: Optional[str] = None,
        proxy_file: Optional[str] = None,
        use_proxies: bool = True
    ):
        """
        Initialize analysis pipeline
        
        Args:
            serp_api_key: API key for SERP service
            proxy_file: Path to proxy file
            use_proxies: Use proxies for scraping
        """
        self.serp_service = get_serp_service(api_key=serp_api_key)
        self.scraping_service = get_scraping_service(
            proxy_file=proxy_file,
            headless=True
        )
        self.embedding_service = get_embedding_service()
        self.scoring_service = get_scoring_service()
        self.use_proxies = use_proxies
    
    async def analyze_query(
        self,
        query: str,
        target_url: Optional[str] = None,
        analyze_top_n: int = 10,
        location: str = "United States"
    ) -> AnalysisPipelineResult:
        """
        Complete analysis workflow for a search query
        
        Args:
            query: Target search query
            target_url: Your URL to analyze (optional)
            analyze_top_n: Number of top competitors to analyze
            location: Geographic location for SERP
            
        Returns:
            AnalysisPipelineResult with complete analysis
        """
        logger.info(
            "analysis_pipeline_started",
            query=query,
            target_url=target_url,
            analyze_top_n=analyze_top_n
        )
        
        # Step 1: Get SERP results
        logger.info("step_1_fetching_serp_results")
        serp_results = await self.serp_service.search(
            query=query,
            location=location,
            num_results=analyze_top_n
        )
        
        if 'error' in serp_results:
            logger.error("serp_fetch_failed", error=serp_results['error'])
            return self._create_error_result(query, serp_results['error'])
        
        competitor_urls = self.serp_service.extract_urls(serp_results, top_n=analyze_top_n)
        logger.info("serp_results_fetched", url_count=len(competitor_urls))
        
        # Step 2: Scrape target URL (if provided)
        target_score = None
        if target_url:
            logger.info("step_2a_scraping_target_url", url=target_url)
            target_content = self.scraping_service.scrape_url(
                target_url,
                use_proxy=self.use_proxies
            )
            
            if 'error' not in target_content:
                target_score = self.scoring_service.score_content(
                    target_content,
                    query=query
                )
                logger.info("target_url_scored", score=target_score.composite_score)
        
        # Step 3: Scrape and analyze competitors
        logger.info("step_2b_scraping_competitors", count=len(competitor_urls))
        competitor_contents = self.scraping_service.scrape_urls_batch(
            competitor_urls,
            use_proxy=self.use_proxies,
            delay_between_requests=2.0
        )
        
        # Step 4: Score all competitors
        logger.info("step_3_scoring_competitors")
        competitors = []
        
        for i, (url, content) in enumerate(zip(competitor_urls, competitor_contents)):
            if 'error' in content:
                logger.warning("competitor_scrape_failed", url=url, error=content['error'])
                continue
            
            try:
                # Score competitor content
                score = self.scoring_service.score_content(content, query=query)
                
                # Get competitor data from SERP
                serp_data = next(
                    (r for r in serp_results['organic_results'] if r['link'] == url),
                    {}
                )
                
                competitors.append(CompetitorAnalysis(
                    position=serp_data.get('position', i + 1),
                    url=url,
                    title=content.get('title', serp_data.get('title', 'N/A')),
                    score=score,
                    content_length=len(content.get('text', '')),
                    chunk_count=len(chunk_for_embeddings(content.get('text', '')))
                ))
                
                logger.info(
                    "competitor_scored",
                    position=i + 1,
                    url=url,
                    score=score.composite_score
                )
                
            except Exception as e:
                logger.error("competitor_scoring_failed", url=url, error=str(e))
        
        # Step 5: Generate insights
        logger.info("step_4_generating_insights")
        insights = self._generate_insights(
            query=query,
            target_score=target_score,
            competitors=competitors
        )
        
        # Step 6: Generate recommendations
        recommendations = self._generate_pipeline_recommendations(
            target_score=target_score,
            competitors=competitors,
            insights=insights
        )
        
        logger.info(
            "analysis_pipeline_complete",
            query=query,
            competitors_analyzed=len(competitors),
            has_target=bool(target_score)
        )
        
        return AnalysisPipelineResult(
            query=query,
            target_url=target_url,
            target_score=target_score,
            competitors=competitors,
            insights=insights,
            recommendations=recommendations
        )
    
    def _generate_insights(
        self,
        query: str,
        target_score: Optional[ContentScore],
        competitors: List[CompetitorAnalysis]
    ) -> Dict:
        """Generate competitive insights from analysis"""
        if not competitors:
            return {'error': 'No competitors analyzed'}
        
        # Competitor statistics
        competitor_scores = [c.score.composite_score for c in competitors]
        
        insights = {
            'query': query,
            'competitor_count': len(competitors),
            'average_competitor_score': sum(competitor_scores) / len(competitor_scores),
            'top_competitor_score': max(competitor_scores),
            'lowest_competitor_score': min(competitor_scores),
            'score_std': __import__('numpy').std(competitor_scores),
        }
        
        # Dimension averages
        dimension_avgs = {
            'metadata_alignment': sum(c.score.metadata_alignment for c in competitors) / len(competitors),
            'hierarchical_decomposition': sum(c.score.hierarchical_decomposition for c in competitors) / len(competitors),
            'thematic_unity': sum(c.score.thematic_unity for c in competitors) / len(competitors),
            'balance': sum(c.score.balance for c in competitors) / len(competitors),
            'query_intent': sum(c.score.query_intent for c in competitors) / len(competitors),
            'structural_coherence': sum(c.score.structural_coherence for c in competitors) / len(competitors),
        }
        insights['dimension_averages'] = dimension_avgs
        
        # Content statistics
        insights['average_content_length'] = sum(c.content_length for c in competitors) / len(competitors)
        insights['average_chunk_count'] = sum(c.chunk_count for c in competitors) / len(competitors)
        
        # Target comparison (if available)
        if target_score:
            insights['target_vs_average'] = {
                'composite_score_diff': target_score.composite_score - insights['average_competitor_score'],
                'seo_score_diff': target_score.seo_score - sum(c.score.seo_score for c in competitors) / len(competitors),
                'position': 'above_average' if target_score.composite_score > insights['average_competitor_score'] else 'below_average'
            }
            
            # Dimension gaps
            insights['dimension_gaps'] = {
                dim: target_score.__dict__[dim] - dimension_avgs[dim]
                for dim in dimension_avgs.keys()
            }
        
        # Top performers
        top_3 = sorted(competitors, key=lambda x: x.score.composite_score, reverse=True)[:3]
        insights['top_performers'] = [
            {
                'position': c.position,
                'url': c.url,
                'score': c.score.composite_score,
                'seo_score': c.score.seo_score
            }
            for c in top_3
        ]
        
        return insights
    
    def _generate_pipeline_recommendations(
        self,
        target_score: Optional[ContentScore],
        competitors: List[CompetitorAnalysis],
        insights: Dict
    ) -> List[str]:
        """Generate strategic recommendations based on complete analysis"""
        recommendations = []
        
        if not competitors:
            return ["No competitor data available for recommendations"]
        
        # If we have target URL
        if target_score and 'target_vs_average' in insights:
            position = insights['target_vs_average']['position']
            score_diff = insights['target_vs_average']['composite_score_diff']
            
            if position == 'below_average':
                recommendations.append(
                    f"Your content scores {abs(score_diff):.1f} points below average competitors. "
                    "Focus on improving weak dimensions."
                )
                
                # Identify weakest dimensions
                dimension_gaps = insights.get('dimension_gaps', {})
                weak_dims = sorted(
                    dimension_gaps.items(),
                    key=lambda x: x[1]
                )[:2]
                
                for dim, gap in weak_dims:
                    if gap < -10:
                        recommendations.append(
                            f"Priority: Improve {dim.replace('_', ' ')} "
                            f"(currently {gap:.1f} points below competitors)"
                        )
            else:
                recommendations.append(
                    f"Your content performs well ({score_diff:.1f} points above average). "
                    "Focus on maintaining quality and targeting additional keywords."
                )
        
        # General competitive insights
        avg_score = insights.get('average_competitor_score', 0)
        top_score = insights.get('top_competitor_score', 0)
        
        if top_score - avg_score > 15:
            recommendations.append(
                "Large quality gap exists between top and average competitors. "
                "Study top performers for best practices."
            )
        
        # Content length insights
        avg_length = insights.get('average_content_length', 0)
        if avg_length > 0:
            if target_score and 'content_length' in insights:
                target_length = sum(c.content_length for c in competitors if c.url == insights.get('target_url', ''))
                if target_length and target_length < avg_length * 0.7:
                    recommendations.append(
                        f"Consider expanding content. Average competitors have "
                        f"{avg_length:.0f} characters vs your {target_length:.0f}"
                    )
        
        # Dimension-specific insights
        dim_avgs = insights.get('dimension_averages', {})
        
        if dim_avgs.get('query_intent', 0) < 65:
            recommendations.append(
                "Overall query intent alignment is low across competitors. "
                "Opportunity to differentiate by better targeting user intent."
            )
        
        if dim_avgs.get('structural_coherence', 0) < 65:
            recommendations.append(
                "Competitors show weak structural coherence. "
                "Improve your content organization for competitive advantage."
            )
        
        return recommendations
    
    def _create_error_result(self, query: str, error: str) -> AnalysisPipelineResult:
        """Create error result"""
        return AnalysisPipelineResult(
            query=query,
            target_url=None,
            target_score=None,
            competitors=[],
            insights={'error': error},
            recommendations=[f"Analysis failed: {error}"]
        )


# Singleton instance
_analysis_pipeline_instance = None


def get_analysis_pipeline(
    serp_api_key: Optional[str] = None,
    proxy_file: Optional[str] = None
) -> AnalysisPipeline:
    """Get or create singleton analysis pipeline instance"""
    global _analysis_pipeline_instance
    
    if _analysis_pipeline_instance is None:
        _analysis_pipeline_instance = AnalysisPipeline(
            serp_api_key=serp_api_key,
            proxy_file=proxy_file
        )
    
    return _analysis_pipeline_instance

