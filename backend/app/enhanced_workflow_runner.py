#!/usr/bin/env python3
"""
Enhanced Workflow Runner with Proxy Scraping
Processes data through each step of the SEO analysis workflow with proper proxy support
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.append('/app')

from app.services.embeddings import get_embedding_service
from app.services.optimization import get_semantic_optimizer
from app.services.scoring import get_scoring_service
from app.services.scraping import get_scraping_service
from app.core.config import settings


class EnhancedWorkflowRunner:
    """
    Enhanced SEO Analysis Workflow Runner
    Features:
    - Keyword-bounded analysis (only competitors for specific query)
    - Resume capability (skip completed steps)
    - Configurable top-N competitors
    - Efficient processing (no duplicate work)
    """
    
    def __init__(self, project_name: str = "500rockets", resume: bool = True, top_n: int = 10):
        self.project_name = project_name
        self.resume = resume
        self.top_n = top_n
        self.project_dir = Path(f"/app/output/projects/{project_name}")
        self.config_file = self.project_dir / "00_config" / "project_config.json"
        
        # Load or create project config
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "project_name": project_name,
                "query": "high quality message building",
                "target_url": "https://500rockets.io/commzone-mtt/",
                "top_n": top_n,
                "status": "initialized",
                "current_step": "00_config",
                "steps_completed": [],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self._save_config()
    
    def _save_config(self):
        """Save project configuration"""
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / "00_config").mkdir(exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def update_status(self, step: str, status: str = "completed"):
        """Update project status"""
        self.config["current_step"] = step
        if step not in self.config["steps_completed"]:
            self.config["steps_completed"].append(step)
        self.config["status"] = status
        self.config["last_updated"] = datetime.now().isoformat()
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    async def step_02_serp_fetching(self):
        """Step 2: Fetch fresh SERP results (resume-aware)"""
        print("🔄 Step 2: SERP API Fetching")
        print("=" * 50)
        
        # Check if we should skip this step
        serp_dir = self.project_dir / "02_serp_results"
        serp_file = serp_dir / "serp_results.json"
        
        if self.resume and serp_file.exists():
            print("⏭️  Skipping SERP fetching - using existing results")
            with open(serp_file, 'r', encoding='utf-8') as f:
                serp_data = json.load(f)
            
            # Extract competitor URLs
            organic_results = serp_data.get('organic_results', [])
            competitor_urls = [result.get('link', '') for result in organic_results[:self.top_n]]
            target_ranking = serp_data.get('target_ranking')
            
            print(f"✅ Loaded {len(competitor_urls)} competitor URLs from existing SERP data")
            if target_ranking:
                print(f"🎯 Target URL ranking: #{target_ranking}")
            else:
                print(f"⚠️  Target URL not in top {self.top_n}")
            
            return competitor_urls, target_ranking
        
        # Fresh SERP fetching
        from app.services.serp import get_serp_service
        serp_service = get_serp_service()
        
        query = self.config["query"]
        target_url = self.config["target_url"]
        
        print(f"🔍 Fetching SERP results for: '{query}'")
        print(f"🎯 Target URL: {target_url}")
        print(f"📊 Top {self.top_n} competitors requested")
        
        # Update project config with new parameters
        self.config["query"] = query
        self.config["target_url"] = target_url
        self.config["last_updated"] = datetime.now().isoformat()
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print(f"🔍 Fetching SERP results for: '{query}'")
        print(f"🎯 Target URL: {target_url}")
        
        try:
            serp_results = await serp_service.search(query, num_results=self.top_n)
            
            if 'error' in serp_results:
                raise Exception(f"SERP API error: {serp_results['error']}")
            
            # Extract URLs from organic results
            organic_results = serp_results.get('organic_results', [])
            competitor_urls = []
            
            # Check if our target URL is in the top N
            target_ranking = None
            for i, result in enumerate(organic_results, 1):
                url = result.get('link', '')  # SERP API uses 'link' field, not 'url'
                competitor_urls.append(url)
                if url == target_url:
                    target_ranking = i
                    print(f"🎯 Target URL found at position #{i}")
            
            if target_ranking is None:
                print(f"⚠️  Target URL not found in top {self.top_n} - will show as 'not ranking'")
            
            print(f"✅ Found {len(competitor_urls)} competitor URLs")
            
            # Save SERP results
            serp_dir = self.project_dir / "02_serp_results"
            serp_dir.mkdir(exist_ok=True)
            
            with open(serp_dir / "serp_results.json", 'w', encoding='utf-8') as f:
                json.dump({
                    "query": query,
                    "target_url": target_url,
                    "target_ranking": target_ranking,
                    "organic_results": organic_results,
                    "full_response": serp_results,
                    "fetched_at": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            with open(serp_dir / "competitor_urls.json", 'w', encoding='utf-8') as f:
                json.dump(competitor_urls, f, indent=2, ensure_ascii=False)
            
            print(f"💾 SERP results saved to: {serp_dir}")
            return competitor_urls, target_ranking
            
        except Exception as e:
            print(f"❌ SERP fetching failed: {e}")
            print("🔄 No fallback URLs available - SERP API is required for fresh analysis")
            raise Exception(f"SERP API failed: {e}. Cannot proceed without competitor URLs.")

    async def step_03_competitor_scraping(self, competitor_urls: list = None, target_ranking: int = None):
        """Step 3: Scrape competitor content with proxy support"""
        print("🔄 Step 3: Competitor Scraping with Proxies")
        print("=" * 50)
        
        # Check if we already have content for this query
        extracted_dir = self.project_dir / "03_competitor_content" / "extracted_content"
        current_query = self.config.get("query", "")
        
        if extracted_dir.exists():
            existing_files = list(extracted_dir.glob("*.json"))
            matching_files = []
            
            for filepath in existing_files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        file_query = data.get('query', '')
                        if file_query == current_query:
                            matching_files.append(filepath)
                except Exception:
                    continue
            
            if matching_files:
                print(f"⏭️  Skipping scraping - found {len(matching_files)} existing files for query: '{current_query}'")
                print("✅ Using existing scraped content")
                return {"successful": len(matching_files), "failed": 0, "total": len(matching_files)}
        
        # Initialize scraping service with proxy support
        proxy_file = settings.PROXY_FILE if settings.USE_PROXIES else None
        print(f"🔧 Proxy configuration:")
        print(f"   USE_PROXIES: {settings.USE_PROXIES}")
        print(f"   PROXY_FILE: {proxy_file}")
        print(f"   DISABLE_DIRECT_CONNECTION: {settings.DISABLE_DIRECT_CONNECTION}")
        print()
        
        scraping_service = get_scraping_service(
            proxy_file=proxy_file,
            headless=True
        )
        
        # Use provided URLs or fallback to original analysis
        if competitor_urls is None:
            # Get competitor URLs from the original analysis
            original_analysis_file = self.project_dir / "08_archive" / "previous_analyses" / "original_analysis_20251015_182119.json"
            
            if not original_analysis_file.exists():
                print("❌ Original analysis file not found. Using existing scraped content.")
                return await self.load_existing_content()
            
            # Load competitor URLs from original analysis
            with open(original_analysis_file, 'r', encoding='utf-16') as f:
                original_data = json.load(f)
            
            competitor_urls = [comp['url'] for comp in original_data.get('competitors', [])]
            target_url = original_data.get('target_url', 'https://500rockets.io')
        else:
            target_url = "https://500rockets.io/commzone-mtt/"
        
        print(f"🎯 Target URL: {target_url}")
        print(f"🔍 Competitor URLs: {len(competitor_urls)}")
        print()
        
        # Scrape target first
        print("📊 Scraping target website...")
        target_result = await scraping_service.scrape_url(
            url=target_url,
            use_proxy=settings.USE_PROXIES,
            max_retries=3
        )
        
        if target_result and target_result.get('text'):
            target_file = self.project_dir / "03_competitor_content" / "extracted_content" / "500rockets.io_commzone-mtt.json"
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_data = {
                "url": target_result['url'],
                "title": target_result['title'],
                "content": target_result['text'],  # Use 'text' field
                "meta_description": target_result.get('meta_description', ''),
                "source": "proxy_scraping",
                "added_at": datetime.now().isoformat(),
                "content_length": len(target_result['text']),
                "word_count": len(target_result['text'].split()),
                "scraping_method": "proxy_enabled",
                "serp_ranking": "not ranking" if target_ranking is None else target_ranking,
                "query": self.config.get('query', 'unknown')
            }
            
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(target_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Target scraped: {len(target_result['text'])} chars")
        else:
            print("❌ Target scraping failed")
        
        print()
        
        # Scrape competitors
        print("🔍 Scraping competitors with proxy support...")
        successful_scrapes = 0
        failed_scrapes = 0
        
        for i, url in enumerate(competitor_urls, 1):
            print(f"[{i}/{len(competitor_urls)}] Scraping {url}")
            
            try:
                result = await scraping_service.scrape_url(
                    url=url,
                    use_proxy=settings.USE_PROXIES,
                    max_retries=3
                )
                
                if result and result.get('text') and len(result['text'].strip()) > 100:
                    # Create filename from URL
                    from urllib.parse import urlparse
                    parsed_url = urlparse(url)
                    filename = parsed_url.netloc.replace('www.', '')
                    if parsed_url.path and parsed_url.path != '/':
                        path_parts = parsed_url.path.strip('/').replace('/', '_')
                        filename += f"_{path_parts}"
                    filename += ".json"
                    
                    # Save competitor data with ranking information
                    competitor_file = self.project_dir / "03_competitor_content" / "extracted_content" / filename
                    competitor_file.parent.mkdir(parents=True, exist_ok=True)
                    competitor_data = {
                        "url": result['url'],
                        "title": result['title'],
                        "content": result['text'],  # Use 'text' field
                        "meta_description": result.get('meta_description', ''),
                        "source": "proxy_scraping",
                        "added_at": datetime.now().isoformat(),
                        "content_length": len(result['text']),
                        "word_count": len(result['text'].split()),
                        "scraping_method": "proxy_enabled",
                        "serp_ranking": i,  # Add ranking position
                        "query": self.config.get('query', 'unknown')
                    }
                    
                    # Save full page backup for auditing/re-analysis
                    backup_file = self.project_dir / "03_competitor_content" / "raw_backups" / filename
                    backup_file.parent.mkdir(exist_ok=True)
                    
                    backup_data = {
                        "url": result['url'],
                        "title": result['title'],
                        "raw_html": result.get('raw_html', ''),  # Full HTML if available
                        "extracted_text": result['text'],
                        "meta_description": result.get('meta_description', ''),
                        "extraction_method": result.get('extraction_method', 'unknown'),
                        "scraping_timestamp": datetime.now().isoformat(),
                        "serp_ranking": i,
                        "query": self.config.get('query', 'unknown'),
                        "content_length": len(result['text']),
                        "word_count": len(result['text'].split())
                    }
                    
                    with open(competitor_file, 'w', encoding='utf-8') as f:
                        json.dump(competitor_data, f, indent=2, ensure_ascii=False)
                    
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(backup_data, f, indent=2, ensure_ascii=False)
                    
                    successful_scrapes += 1
                    print(f"  ✅ Success: {len(result['text'])} chars, {len(result['text'].split())} words")
                else:
                    failed_scrapes += 1
                    print(f"  ❌ Failed: No content extracted")
                    
            except Exception as e:
                failed_scrapes += 1
                print(f"  ❌ Error: {str(e)[:100]}...")
            
            print()
            
            # Small delay between requests
            await asyncio.sleep(2)
        
        print(f"✅ Scraping complete: {successful_scrapes} successful, {failed_scrapes} failed")
        self.update_status("03_competitor_content")
        
        return {
            "successful": successful_scrapes,
            "failed": failed_scrapes,
            "total": len(competitor_urls)
        }
    
    async def load_existing_content(self):
        """Load existing content if scraping is skipped (keyword-bounded)"""
        print("📁 Loading existing competitor content...")
        
        extracted_dir = self.project_dir / "03_competitor_content" / "extracted_content"
        competitors = []
        target = None
        current_query = self.config.get("query", "")
        
        for filename in os.listdir(extracted_dir):
            if filename.endswith('.json'):
                filepath = extracted_dir / filename
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Only load content that matches current query
                    file_query = data.get('query', '')
                    if file_query != current_query:
                        print(f"⏭️  Skipping {filename} - different query ({file_query})")
                        continue
                    
                    if '500rockets.io' in filename:
                        target = data
                    else:
                        competitors.append(data)
        
        print(f"✅ Loaded {len(competitors)} competitors and target for query: '{current_query}'")
        return {"successful": len(competitors), "failed": 0, "total": len(competitors)}
    
    async def step_04_content_processing(self):
        """Step 4: Process content through embeddings and semantic analysis"""
        print("🔄 Step 4: Content Processing")
        print("=" * 50)
        
        # Load competitor content
        extracted_dir = self.project_dir / "03_competitor_content" / "extracted_content"
        competitors = []
        target = None
        
        for filename in os.listdir(extracted_dir):
            if filename.endswith('.json'):
                filepath = extracted_dir / filename
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if '500rockets.io' in filename:
                        target = data
                    else:
                        competitors.append(data)
        
        print(f"✅ Loaded {len(competitors)} competitors and target")
        
        # Initialize services
        embedding_service = get_embedding_service()
        semantic_optimizer = await get_semantic_optimizer()
        
        # Process target content
        print("🧠 Processing target content...")
        target_phrases = semantic_optimizer._extract_phrases(target['content'])
        target_embeddings = embedding_service.encode(target_phrases)
        
        # Save target processing results
        target_processing = {
            "url": target['url'],
            "phrases": target_phrases,
            "embeddings": target_embeddings.tolist(),  # Convert numpy array to list
            "phrase_count": len(target_phrases),
            "processed_at": datetime.now().isoformat()
        }
        
        processing_dir = self.project_dir / "04_content_processing"
        processing_dir.mkdir(parents=True, exist_ok=True)
        with open(processing_dir / "target_processing.json", 'w', encoding='utf-8') as f:
            json.dump(target_processing, f, indent=2, ensure_ascii=False)
        
        # Process competitor content
        print("🧠 Processing competitor content...")
        competitor_processing = []
        
        for competitor in competitors:
            phrases = semantic_optimizer._extract_phrases(competitor['content'])
            embeddings = embedding_service.encode(phrases)
            
            competitor_data = {
                "url": competitor['url'],
                "filename": competitor.get('filename', ''),
                "phrases": phrases,
                "embeddings": embeddings.tolist(),  # Convert numpy array to list
                "phrase_count": len(phrases),
                "processed_at": datetime.now().isoformat()
            }
            
            competitor_processing.append(competitor_data)
        
        # Save competitor processing results
        with open(processing_dir / "competitor_processing.json", 'w', encoding='utf-8') as f:
            json.dump(competitor_processing, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Processed {len(competitor_processing)} competitors")
        self.update_status("04_content_processing")
        
        return {
            "target": target_processing,
            "competitors": competitor_processing
        }
    
    async def step_05_competitive_analysis(self, processing_results):
        """Step 5: Competitive analysis and scoring"""
        print("🔄 Step 5: Competitive Analysis")
        print("=" * 50)
        
        # Initialize scoring service
        scoring_service = get_scoring_service()
        
        # Score target
        print("📊 Scoring target content...")
        target_score = scoring_service.score_content(
            {
                "text": " ".join(processing_results["target"]["phrases"]),
                "title": "CommZone - MTT | 500 Rockets Marketing",
                "description": "High quality message building services"
            },
            processing_results["target"]["url"]
        )
        
        # Score competitors
        print("📊 Scoring competitor content...")
        competitor_scores = []
        
        for competitor in processing_results["competitors"]:
            # Reconstruct content from phrases (processing data has phrases, not content)
            competitor_content = {
                "text": " ".join(competitor["phrases"]),
                "title": competitor.get("title", ""),
                "description": competitor.get("meta_description", "")
            }
            
            score = scoring_service.score_content(
                competitor_content,
                competitor["url"]
            )
            
            competitor_scores.append({
                "url": competitor["url"],
                "filename": competitor.get("filename", ""),
                "score": {
                    "metadata_alignment": score.metadata_alignment,
                    "hierarchical_decomposition": score.hierarchical_decomposition,
                    "thematic_unity": score.thematic_unity,
                    "balance": score.balance,
                    "query_intent": score.query_intent,
                    "structural_coherence": score.structural_coherence,
                    "composite_score": score.composite_score,
                    "seo_score": score.seo_score
                },
                "phrase_count": competitor["phrase_count"]
            })
        
        # Create competitive analysis
        analysis = {
            "query": self.config["query"],
            "target_url": self.config["target_url"],
            "target_score": {
                "metadata_alignment": target_score.metadata_alignment,
                "hierarchical_decomposition": target_score.hierarchical_decomposition,
                "thematic_unity": target_score.thematic_unity,
                "balance": target_score.balance,
                "query_intent": target_score.query_intent,
                "structural_coherence": target_score.structural_coherence,
                "composite_score": target_score.composite_score,
                "seo_score": target_score.seo_score
            },
            "competitors": competitor_scores,
            "analysis_metadata": {
                "total_competitors": len(competitor_scores),
                "analysis_date": datetime.now().isoformat(),
                "project_name": self.project_name
            }
        }
        
        # Save analysis results
        analysis_dir = self.project_dir / "05_competitive_analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        with open(analysis_dir / "competitive_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analyzed {len(competitor_scores)} competitors")
        self.update_status("05_competitive_analysis")
        
        return analysis
    
    async def step_06_optimization(self, processing_results, analysis_results):
        """Step 6: Generate optimization recommendations"""
        print("🔄 Step 6: Optimization Analysis")
        print("=" * 50)
        
        # Initialize services
        embedding_service = get_embedding_service()
        semantic_optimizer = await get_semantic_optimizer()
        
        # Extract all phrases
        all_phrases = []
        phrase_sources = {}
        
        # Add target phrases
        target_phrases = processing_results["target"]["phrases"]
        all_phrases.extend(target_phrases)
        for phrase in target_phrases:
            phrase_sources[phrase] = phrase_sources.get(phrase, []) + ['target']
        
        # Add competitor phrases
        for competitor in processing_results["competitors"]:
            competitor_phrases = competitor["phrases"]
            all_phrases.extend(competitor_phrases)
            for phrase in competitor_phrases:
                phrase_sources[phrase] = phrase_sources.get(phrase, []) + [competitor.get("filename", "unknown")]
        
        # Remove duplicates
        unique_phrases = list(set(all_phrases))
        
        # Generate embeddings for all phrases
        print("🧠 Generating embeddings for semantic analysis...")
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(unique_phrases), batch_size):
            batch = unique_phrases[i:i+batch_size]
            batch_embeddings = embedding_service.encode(batch)
            all_embeddings.extend(batch_embeddings)
            print(f"  Processed {min(i+batch_size, len(unique_phrases))}/{len(unique_phrases)} phrases")
        
        # Create phrase-to-embedding mapping
        phrase_embeddings = dict(zip(unique_phrases, all_embeddings))
        
        # Generate query embedding
        query_embedding = embedding_service.encode([self.config["query"]])[0]
        
        # Analyze semantic gaps
        print("🎯 Analyzing semantic gaps...")
        
        # Get target content string
        target_content = ""
        competitor_contents = []
        
        # Load target content
        target_file = self.project_dir / "03_competitor_content" / "extracted_content" / "500rockets.io_commzone-mtt.json"
        if target_file.exists():
            with open(target_file, 'r', encoding='utf-8') as f:
                target_data = json.load(f)
                target_content = target_data.get('content', '')
        
        # Load competitor contents
        extracted_dir = self.project_dir / "03_competitor_content" / "extracted_content"
        for filename in os.listdir(extracted_dir):
            if filename.endswith('.json') and '500rockets.io' not in filename:
                filepath = extracted_dir / filename
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_query = data.get('query', '')
                    if file_query == self.config.get("query", ""):
                        competitor_contents.append(data.get('content', ''))
        
        semantic_gaps_result = await semantic_optimizer.analyze_semantic_gaps(
            target_content, competitor_contents, self.config["query"]
        )
        
        # Extract the list from the dictionary result
        semantic_gaps = semantic_gaps_result.get('missing_concepts', [])
        
        # Sort by estimated impact
        semantic_gaps.sort(key=lambda x: x.get('estimated_impact', 0), reverse=True)
        
        # Generate recommendations
        top_gaps = semantic_gaps[:20]
        recommendations = {
            "query": self.config["query"],
            "target_url": self.config["target_url"],
            "total_gaps_found": len(semantic_gaps),
            "top_gaps": top_gaps,
            "estimated_improvement": sum(gap.get('estimated_impact', 0) for gap in top_gaps[:10]),
            "recommendations": [
                f"Add '{gap['phrase']}' to improve semantic alignment (estimated +{gap.get('estimated_impact', 0):.1f} points)"
                for gap in top_gaps[:10]
            ],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Save optimization results
        optimization_dir = self.project_dir / "06_optimization"
        optimization_dir.mkdir(parents=True, exist_ok=True)
        
        with open(optimization_dir / "semantic_gaps.json", 'w', encoding='utf-8') as f:
            json.dump(semantic_gaps, f, indent=2, ensure_ascii=False)
        
        with open(optimization_dir / "recommendations.json", 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Found {len(semantic_gaps)} semantic gaps")
        print(f"💡 Generated {len(recommendations['recommendations'])} recommendations")
        self.update_status("06_optimization")
        
        return recommendations
    
    async def step_07_final_reports(self, analysis_results, optimization_results):
        """Step 7: Generate final reports"""
        print("🔄 Step 7: Final Reports")
        print("=" * 50)
        
        # Create executive summary
        executive_summary = f"""# Executive Summary - {self.project_name}

## Project Overview
- **Target Website**: {self.config['target_url']}
- **Search Query**: {self.config['query']}
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Competitors Analyzed**: {len(analysis_results['competitors'])}

## Current Rankings

### Target URL Performance
- **Current Ranking**: {analysis_results.get('target_ranking', 'Not ranking in top 10')}
- **Target URL**: {self.config['target_url']}

### Competitor Rankings
"""
        
        # Add competitor rankings
        for competitor in analysis_results.get('competitors', []):
            ranking = competitor.get('serp_ranking', 'Unknown')
            url = competitor.get('url', 'Unknown')
            title = competitor.get('title', 'Unknown')[:50] + "..." if len(competitor.get('title', '')) > 50 else competitor.get('title', 'Unknown')
            executive_summary += f"- **#{ranking}**: {title} ({url})\n"
        
        executive_summary += f"""
## Key Findings

### Target Performance
- **Composite Score**: {analysis_results['target_score'].get('composite_score', 'N/A'):.1f}
- **SEO Score**: {analysis_results['target_score'].get('seo_score', 'N/A'):.1f}

### Competitive Position
- **Average Competitor Score**: {sum(c['score'].get('composite_score', 0) for c in analysis_results['competitors']) / len(analysis_results['competitors']):.1f}
- **Top Competitor Score**: {max(c['score'].get('composite_score', 0) for c in analysis_results['competitors']):.1f}

### Optimization Opportunities
- **Semantic Gaps Identified**: {optimization_results['total_gaps_found']}
- **Estimated Improvement**: +{optimization_results['estimated_improvement']:.1f} points
- **Top Recommendations**: {len(optimization_results['recommendations'])}

## Immediate Actions
1. Implement top 10 semantic gap recommendations
2. Analyze top-performing competitors for content structure
3. Optimize metadata alignment based on competitive analysis

## Next Steps
1. Review detailed analysis in 05_competitive_analysis/
2. Implement recommendations from 06_optimization/
3. Monitor performance improvements
4. Schedule follow-up analysis

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Save executive summary
        reports_dir = self.project_dir / "07_final_reports"
        (reports_dir / "executive_summary").mkdir(parents=True, exist_ok=True)
        with open(reports_dir / "executive_summary" / "executive_summary.md", 'w', encoding='utf-8') as f:
            f.write(executive_summary)
        
        # Create implementation guide
        implementation_guide = f"""# Implementation Guide - {self.project_name}

## Quick Start
1. Review executive summary
2. Implement top 10 recommendations
3. Monitor results

## Top Recommendations
"""
        
        for i, rec in enumerate(optimization_results['recommendations'][:10], 1):
            implementation_guide += f"{i}. {rec}\n"
        
        implementation_guide += f"""
## Files to Review
- Executive Summary: `07_final_reports/executive_summary/executive_summary.md`
- Detailed Analysis: `05_competitive_analysis/competitive_analysis.json`
- Optimization Recommendations: `06_optimization/recommendations.json`
- Semantic Gaps: `06_optimization/semantic_gaps.json`

## Project Structure
```
/app/projects/{self.project_name}/
├── 00_config/           # Project configuration
├── 01_target_analysis/  # Target website analysis
├── 02_serp_results/     # SERP API results
├── 03_competitor_content/ # Competitor content (PROXY SCRAPED)
├── 04_content_processing/ # Content processing
├── 05_competitive_analysis/ # Competitive analysis
├── 06_optimization/     # Optimization recommendations
├── 07_final_reports/    # Final reports
└── 08_archive/          # Archived data
```

---
*Guide generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        (reports_dir / "implementation_guide").mkdir(parents=True, exist_ok=True)
        with open(reports_dir / "implementation_guide" / "implementation_guide.md", 'w', encoding='utf-8') as f:
            f.write(implementation_guide)
        
        print("✅ Generated executive summary and implementation guide")
        self.update_status("07_final_reports", "completed")
    
    async def run_complete_workflow(self, use_proxies: bool = True):
        """Run the complete workflow from step 3 to 7"""
        print("=" * 80)
        print("  COMPLETE SEO ANALYSIS WORKFLOW WITH PROXY SUPPORT")
        print("=" * 80)
        print(f"Project: {self.project_name}")
        print(f"Query: {self.config['query']}")
        print(f"Target: {self.config['target_url']}")
        print(f"Use Proxies: {use_proxies}")
        print()
        
        # Step 2: SERP Fetching
        competitor_urls, target_ranking = await self.step_02_serp_fetching()
        print()
        
        # Step 3: Competitor Scraping (with proxies)
        if use_proxies:
            scraping_results = await self.step_03_competitor_scraping(competitor_urls, target_ranking)
            print()
        else:
            scraping_results = await self.load_existing_content()
            print()
        
        # Step 4: Content Processing
        processing_results = await self.step_04_content_processing()
        print()
        
        # Step 5: Competitive Analysis
        analysis_results = await self.step_05_competitive_analysis(processing_results)
        print()
        
        # Step 6: Optimization
        optimization_results = await self.step_06_optimization(processing_results, analysis_results)
        print()
        
        # Step 7: Final Reports
        await self.step_07_final_reports(analysis_results, optimization_results)
        print()
        
        print("=" * 80)
        print("  WORKFLOW COMPLETE")
        print("=" * 80)
        print(f"📁 Project location: {self.project_dir}")
        print(f"🔍 Scraping results: {scraping_results['successful']} successful, {scraping_results['failed']} failed")
        print(f"📊 Analysis complete: {len(analysis_results['competitors'])} competitors")
        print(f"🎯 Semantic gaps found: {optimization_results['total_gaps_found']}")
        print(f"💡 Recommendations generated: {len(optimization_results['recommendations'])}")
        print(f"📈 Estimated improvement: +{optimization_results['estimated_improvement']:.1f} points")
        print()
        print("📋 Key files:")
        print("   📊 Executive Summary: 07_final_reports/executive_summary/executive_summary.md")
        print("   💡 Recommendations: 06_optimization/recommendations.json")
        print("   🔍 Semantic Gaps: 06_optimization/semantic_gaps.json")
        print()


async def main():
    """Main function to run the workflow with configurable parameters"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced SEO Analysis Workflow')
    parser.add_argument('--project', default='500rockets', help='Project name')
    parser.add_argument('--resume', action='store_true', default=True, help='Resume from existing data')
    parser.add_argument('--fresh', action='store_true', help='Force fresh run (overrides resume)')
    parser.add_argument('--top-n', type=int, default=10, help='Number of top competitors to analyze')
    parser.add_argument('--query', help='Search query (overrides config)')
    parser.add_argument('--target-url', help='Target URL (overrides config)')
    
    args = parser.parse_args()
    
    # Determine resume behavior
    resume = args.resume and not args.fresh
    
    print("=" * 80)
    print("  ENHANCED SEO ANALYSIS WORKFLOW")
    print("=" * 80)
    print(f"Project: {args.project}")
    print(f"Resume: {resume}")
    print(f"Top N: {args.top_n}")
    print()
    
    runner = EnhancedWorkflowRunner(
        project_name=args.project,
        resume=resume,
        top_n=args.top_n
    )
    
    # Override config if provided
    if args.query:
        runner.config["query"] = args.query
    if args.target_url:
        runner.config["target_url"] = args.target_url
    
    await runner.run_complete_workflow(use_proxies=True)


if __name__ == "__main__":
    asyncio.run(main())
