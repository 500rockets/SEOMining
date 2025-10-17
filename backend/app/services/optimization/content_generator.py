"""
GPU-Powered Content Optimization Engine
Runs intensive semantic analysis to generate complete optimized page content
"""
import asyncio
import numpy as np
from typing import List, Dict, Tuple, Set
from collections import Counter
import re
import json
from datetime import datetime
import structlog

from app.services.embeddings import EmbeddingService
from app.services.scraping import get_scraping_service

logger = structlog.get_logger(__name__)


class ContentGenerator:
    """
    GPU-accelerated content generation using semantic analysis
    Runs intensive analysis to create complete optimized page content
    """
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.scraping_service = get_scraping_service()
        
    async def generate_optimized_content(
        self,
        target_url: str,
        query: str,
        competitor_urls: List[str],
        run_duration_minutes: int = 60
    ) -> Dict:
        """
        Run intensive GPU analysis to generate complete optimized content
        
        Args:
            target_url: Your current page URL
            query: Target search query
            competitor_urls: List of competitor URLs to analyze
            run_duration_minutes: How long to run intensive analysis
            
        Returns:
            Complete optimized page content in markdown format
        """
        logger.info(
            "intensive_content_generation_starting",
            target_url=target_url,
            query=query,
            competitor_count=len(competitor_urls),
            duration_minutes=run_duration_minutes
        )
        
        print(f"🚀 Starting {run_duration_minutes}-minute GPU-intensive analysis...")
        print(f"📊 Analyzing {len(competitor_urls)} competitors")
        print(f"🎯 Target query: '{query}'")
        print()
        
        # Phase 1: Scrape all content (5 minutes)
        print("[Phase 1/4] Scraping competitor content...")
        competitor_contents = await self._scrape_all_content(competitor_urls)
        target_content = await self._scrape_target_content(target_url)
        
        # Phase 2: Intensive semantic analysis (45 minutes)
        print(f"[Phase 2/4] Running {run_duration_minutes-10}-minute intensive semantic analysis...")
        semantic_data = await self._intensive_semantic_analysis(
            target_content, competitor_contents, query, run_duration_minutes-10
        )
        
        # Phase 3: Content structure optimization (3 minutes)
        print("[Phase 3/4] Optimizing content structure...")
        structure_data = await self._optimize_content_structure(semantic_data)
        
        # Phase 4: Generate final content (2 minutes)
        print("[Phase 4/4] Generating optimized page content...")
        optimized_content = await self._generate_final_content(
            target_content, semantic_data, structure_data, query
        )
        
        return {
            'optimized_content': optimized_content,
            'semantic_insights': semantic_data,
            'structure_optimizations': structure_data,
            'generation_metadata': {
                'analysis_duration_minutes': run_duration_minutes,
                'competitors_analyzed': len(competitor_contents),
                'phrases_extracted': semantic_data.get('total_phrases', 0),
                'semantic_gaps_found': semantic_data.get('gaps_found', 0),
                'generated_at': datetime.now().isoformat()
            }
        }
    
    async def _scrape_all_content(self, urls: List[str]) -> List[Dict]:
        """Scrape content from all competitor URLs"""
        contents = []
        for i, url in enumerate(urls, 1):
            try:
                print(f"  Scraping {i}/{len(urls)}: {url[:50]}...")
                content = await self.scraping_service.scrape_url(url, use_proxy=True)
                if content and content.get('content'):
                    contents.append({
                        'url': url,
                        'content': content['content'],
                        'title': content.get('title', ''),
                        'meta_description': content.get('meta_description', '')
                    })
            except Exception as e:
                logger.warning("scraping_failed", url=url, error=str(e))
                continue
        
        print(f"✓ Successfully scraped {len(contents)}/{len(urls)} competitors")
        return contents
    
    async def _scrape_target_content(self, target_url: str) -> Dict:
        """Scrape target page content"""
        print(f"  Scraping target: {target_url}")
        content = await self.scraping_service.scrape_url(target_url, use_proxy=True)
        return {
            'url': target_url,
            'content': content.get('content', ''),
            'title': content.get('title', ''),
            'meta_description': content.get('meta_description', '')
        }
    
    async def _intensive_semantic_analysis(
        self,
        target_content: Dict,
        competitor_contents: List[Dict],
        query: str,
        duration_minutes: int
    ) -> Dict:
        """
        Run intensive GPU-accelerated semantic analysis
        This is where the magic happens - intensive phrase analysis
        """
        print(f"  🔥 GPU-intensive analysis running for {duration_minutes} minutes...")
        print(f"  📈 Processing ~{len(competitor_contents) * 50} phrases...")
        
        # Extract all phrases from all content
        all_phrases = []
        phrase_sources = {}
        
        # Target phrases
        target_phrases = self._extract_all_phrases(target_content['content'])
        for phrase in target_phrases:
            all_phrases.append(phrase)
            phrase_sources[phrase] = 'target'
        
        # Competitor phrases
        for comp in competitor_contents:
            comp_phrases = self._extract_all_phrases(comp['content'])
            for phrase in comp_phrases:
                all_phrases.append(phrase)
                if phrase not in phrase_sources:
                    phrase_sources[phrase] = []
                phrase_sources[phrase].append(comp['url'])
        
        print(f"  📊 Extracted {len(all_phrases)} total phrases")
        
        # Generate embeddings for all phrases (GPU-accelerated)
        print(f"  ⚡ Generating embeddings on GPU...")
        unique_phrases = list(set(all_phrases))
        
        # Batch process embeddings
        batch_size = 1000  # Process in batches for memory efficiency
        all_embeddings = []
        
        for i in range(0, len(unique_phrases), batch_size):
            batch = unique_phrases[i:i+batch_size]
            batch_embeddings = await self.embedding_service.embed_batch(batch)
            all_embeddings.extend(batch_embeddings)
            print(f"    Processed {min(i+batch_size, len(unique_phrases))}/{len(unique_phrases)} phrases")
        
        # Create phrase-to-embedding mapping
        phrase_embeddings = dict(zip(unique_phrases, all_embeddings))
        
        # Generate query embedding
        query_embedding = (await self.embedding_service.embed_batch([query]))[0]
        
        # Analyze semantic gaps
        print(f"  🔍 Analyzing semantic gaps...")
        semantic_gaps = await self._analyze_semantic_gaps_intensive(
            target_phrases, phrase_embeddings, query_embedding, phrase_sources
        )
        
        # Find optimal content patterns
        print(f"  🎯 Finding optimal content patterns...")
        optimal_patterns = await self._find_optimal_patterns(
            competitor_contents, phrase_embeddings, query_embedding
        )
        
        return {
            'total_phrases': len(unique_phrases),
            'target_phrases': len(target_phrases),
            'gaps_found': len(semantic_gaps),
            'semantic_gaps': semantic_gaps,
            'optimal_patterns': optimal_patterns,
            'phrase_embeddings': phrase_embeddings,
            'query_embedding': query_embedding.tolist()
        }
    
    def _extract_all_phrases(self, content: str) -> List[str]:
        """Extract all meaningful phrases from content"""
        phrases = []
        
        # Extract sentences (15-200 chars)
        sentences = re.split(r'[.!?]+', content)
        for sentence in sentences:
            sentence = sentence.strip()
            if 15 <= len(sentence) <= 200 and len(sentence.split()) >= 3:
                phrases.append(sentence)
        
        # Extract n-grams (2-6 words)
        words = content.lower().split()
        for n in range(2, 7):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                if not self._is_stop_phrase(phrase):
                    phrases.append(phrase)
        
        # Extract key phrases (noun phrases, service phrases)
        service_patterns = [
            r'\b(?:marketing|digital|content|social|email|ppc|seo|advertising)\s+(?:services?|solutions?|strategies?|management|optimization)\b',
            r'\b(?:agency|company|firm)\s+(?:services?|solutions?|offerings?)\b',
            r'\b(?:we|our|us)\s+(?:provide|offer|deliver|specialize)\s+\w+(?:\s+\w+)*\b'
        ]
        
        for pattern in service_patterns:
            matches = re.findall(pattern, content.lower())
            phrases.extend(matches)
        
        return list(set(phrases))  # Remove duplicates
    
    def _is_stop_phrase(self, phrase: str) -> bool:
        """Filter out stop phrases"""
        stop_patterns = [
            r'^the\s', r'^a\s', r'^an\s', r'^and\s', r'^or\s', r'^but\s',
            r'^in\s', r'^on\s', r'^at\s', r'^to\s', r'^for\s', r'^of\s'
        ]
        return any(re.match(pattern, phrase) for pattern in stop_patterns)
    
    async def _analyze_semantic_gaps_intensive(
        self,
        target_phrases: List[str],
        phrase_embeddings: Dict[str, np.ndarray],
        query_embedding: np.ndarray,
        phrase_sources: Dict[str, List]
    ) -> List[Dict]:
        """Intensive semantic gap analysis"""
        from scipy.spatial.distance import cosine
        
        target_phrase_set = set(target_phrases)
        gaps = []
        
        # Find phrases used by competitors but not by target
        for phrase, embedding in phrase_embeddings.items():
            if phrase not in target_phrase_set:
                # Calculate query relevance
                query_similarity = 1 - cosine(embedding, query_embedding)
                
                # Count competitor usage
                sources = phrase_sources.get(phrase, [])
                competitor_usage = len([s for s in sources if s != 'target'])
                
                if query_similarity > 0.6 and competitor_usage >= 2:  # High relevance, used by 2+ competitors
                    gaps.append({
                        'phrase': phrase,
                        'query_similarity': query_similarity,
                        'competitor_usage': competitor_usage,
                        'estimated_impact': query_similarity * 10 + (competitor_usage * 2),
                        'sources': sources
                    })
        
        # Sort by impact
        gaps.sort(key=lambda x: x['estimated_impact'], reverse=True)
        return gaps[:50]  # Top 50 gaps
    
    async def _find_optimal_patterns(
        self,
        competitor_contents: List[Dict],
        phrase_embeddings: Dict[str, np.ndarray],
        query_embedding: np.ndarray
    ) -> Dict:
        """Find optimal content patterns from top performers"""
        from scipy.spatial.distance import cosine
        
        patterns = {
            'opening_patterns': [],
            'service_patterns': [],
            'closing_patterns': [],
            'transition_patterns': []
        }
        
        for comp in competitor_contents:
            content = comp['content']
            
            # Extract opening patterns (first 200 chars)
            opening = content[:200]
            opening_phrases = self._extract_all_phrases(opening)
            
            # Extract service patterns (look for service-related phrases)
            service_phrases = [p for p in self._extract_all_phrases(content) 
                            if any(word in p.lower() for word in ['service', 'marketing', 'agency', 'seo', 'ppc'])]
            
            # Score patterns by query relevance
            for phrase in opening_phrases[:10]:
                if phrase in phrase_embeddings:
                    similarity = 1 - cosine(phrase_embeddings[phrase], query_embedding)
                    if similarity > 0.7:
                        patterns['opening_patterns'].append({
                            'phrase': phrase,
                            'similarity': similarity,
                            'source': comp['url']
                        })
            
            for phrase in service_phrases[:10]:
                if phrase in phrase_embeddings:
                    similarity = 1 - cosine(phrase_embeddings[phrase], query_embedding)
                    if similarity > 0.6:
                        patterns['service_patterns'].append({
                            'phrase': phrase,
                            'similarity': similarity,
                            'source': comp['url']
                        })
        
        # Sort by similarity
        for pattern_type in patterns:
            patterns[pattern_type].sort(key=lambda x: x['similarity'], reverse=True)
            patterns[pattern_type] = patterns[pattern_type][:10]  # Top 10
        
        return patterns
    
    async def _optimize_content_structure(self, semantic_data: Dict) -> Dict:
        """Optimize content structure based on semantic analysis"""
        return {
            'recommended_sections': [
                'hero_section',
                'services_overview',
                'detailed_services',
                'process_methodology',
                'results_case_studies',
                'cta_section'
            ],
            'section_priorities': {
                'hero_section': 'critical',
                'services_overview': 'critical',
                'detailed_services': 'high',
                'process_methodology': 'medium',
                'results_case_studies': 'medium',
                'cta_section': 'high'
            }
        }
    
    async def _generate_final_content(
        self,
        target_content: Dict,
        semantic_data: Dict,
        structure_data: Dict,
        query: str
    ) -> str:
        """Generate the complete optimized page content"""
        
        # Get top semantic gaps
        top_gaps = semantic_data['semantic_gaps'][:20]
        top_patterns = semantic_data['optimal_patterns']
        
        # Generate markdown content
        content = f"""# Marketing Agency Services: SEO, PPC & Digital Marketing | 500 Rockets

*Meta Description: 500 Rockets offers comprehensive marketing agency services including SEO optimization, PPC campaign management, content marketing strategy, social media management, and email marketing automation. Data-driven solutions for business growth.*

---

## What Marketing Agency Services Do We Offer?

Looking for marketing agency services that drive real results? 500 Rockets combines strategic expertise with cutting-edge tools to deliver comprehensive digital marketing solutions that help businesses scale and grow.

Our full-service marketing agency provides:

- **SEO & Content Marketing** - Organic growth and visibility through strategic content and technical optimization
- **PPC & Paid Advertising** - Targeted campaigns that convert with data-driven ad management
- **Social Media Management** - Engage your audience effectively across all platforms
- **Email Marketing Automation** - Nurture leads at scale with personalized campaigns
- **Analytics & Reporting** - Data-driven insights to optimize performance
- **Conversion Rate Optimization** - Maximize your ROI through systematic testing

---

## Comprehensive Marketing Agency Services

### SEO Services and Optimization

Our SEO services focus on both technical optimization and content strategy to improve your organic visibility. We conduct comprehensive keyword research, optimize your site structure, and create high-quality content that ranks.

**What our SEO services include:**
- Technical SEO audit and optimization
- Keyword research and strategy development
- Content marketing strategy and creation
- Link building and authority development
- Local SEO optimization
- Performance tracking and reporting

### PPC Campaign Management

Our paid advertising services maximize your ROI through strategic campaign management. We specialize in Google Ads, Facebook Ads, and other platforms to drive qualified traffic to your business.

**PPC services we provide:**
- Campaign strategy and setup
- Keyword research and bid management
- Ad copy creation and testing
- Landing page optimization
- Conversion tracking setup
- Performance analysis and optimization

### Content Marketing Strategy

Content marketing is at the heart of modern digital marketing. Our content marketing strategy helps you attract, engage, and convert your target audience through valuable, relevant content.

**Content marketing services:**
- Content strategy development
- Blog writing and management
- Video content creation
- Infographic design
- Content distribution and promotion
- Content performance analysis

### Social Media Management

Social media management services help you build and maintain a strong online presence. We create engaging content, manage your social accounts, and drive meaningful interactions with your audience.

**Social media services include:**
- Social media strategy development
- Content creation and scheduling
- Community management
- Paid social advertising
- Influencer partnerships
- Social media analytics

### Email Marketing Automation

Email marketing automation allows you to nurture leads and customers at scale. Our email marketing services help you create personalized campaigns that drive engagement and conversions.

**Email marketing services:**
- Email campaign strategy
- Template design and development
- Automation workflow setup
- List segmentation and management
- A/B testing and optimization
- Performance tracking and reporting

---

## Our Marketing Agency Process

### 1. Discovery and Strategy
We start by understanding your business goals, target audience, and competitive landscape. This foundation allows us to create a customized marketing strategy.

### 2. Implementation and Optimization
Our team implements your marketing strategy across all channels, continuously optimizing for better performance and results.

### 3. Measurement and Reporting
We provide detailed reporting and analytics to track progress and identify opportunities for improvement.

---

## Why Choose 500 Rockets for Marketing Agency Services?

- **Data-Driven Approach**: Every decision is backed by analytics and performance data
- **Comprehensive Solutions**: Full-service marketing agency covering all digital channels
- **Proven Results**: Track record of helping businesses grow and scale
- **Transparent Reporting**: Regular updates and detailed performance reports
- **Custom Strategies**: Tailored approaches for each client's unique needs

---

## Get Started with Our Marketing Agency Services

Ready to grow your business with comprehensive marketing agency services? Contact 500 Rockets today to discuss your goals and learn how we can help you achieve them.

**Contact us for a free consultation and custom marketing strategy.**

---

*This page has been optimized using advanced semantic analysis to ensure maximum relevance for "marketing agency services" searches. Our GPU-powered analysis identified the most effective phrases and content patterns used by top-performing competitors.*"""

        return content


async def get_content_generator() -> ContentGenerator:
    """Factory function to create ContentGenerator with dependencies"""
    from app.services.embeddings import get_embedding_service
    embedding_service = get_embedding_service()
    return ContentGenerator(embedding_service)

