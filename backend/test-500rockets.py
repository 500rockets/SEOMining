#!/usr/bin/env python
"""
Real-world test: Analyze 500rockets.io against competitors
"""
import sys
sys.path.insert(0, '/app')

import asyncio
import json
from app.services.analysis import get_analysis_pipeline
from app.services.serp import get_serp_service
from app.services.scraping import get_scraping_service
from app.services.embeddings import get_embedding_service
from app.services.scoring import get_scoring_service

async def analyze_500rockets():
    """
    Run complete competitive analysis for 500rockets.io
    """
    print("=" * 70)
    print("  🚀 500ROCKETS.IO - COMPETITIVE SEO ANALYSIS")
    print("=" * 70)
    print()
    
    # Configuration
    target_url = "https://500rockets.io"
    query = "marketing agency services"  # Primary service offering
    analyze_top_n = 10
    
    print(f"Target URL: {target_url}")
    print(f"Query: '{query}'")
    print(f"Analyzing top {analyze_top_n} competitors")
    print()
    print("-" * 70)
    
    try:
        # Initialize services
        print("\n[1/7] Initializing services...")
        serp_service = get_serp_service()
        scraping_service = get_scraping_service(proxy_file="/app/config/proxies.txt")
        embedding_service = get_embedding_service()
        scoring_service = get_scoring_service()
        
        print("✓ All services initialized")
        print(f"  - GPU Device: {embedding_service.device}")
        if scraping_service.proxy_manager:
            print(f"  - Proxies: {len(scraping_service.proxy_manager.proxies)} loaded")
        
        # Step 1: Fetch SERP results
        print("\n[2/7] Fetching SERP results...")
        competitor_urls = await serp_service.fetch_top_n_urls(query, num_results=analyze_top_n + 1)
        
        # Remove target if it appears, keep top N
        competitor_urls = [url for url in competitor_urls if target_url not in url][:analyze_top_n]
        
        print(f"✓ Found {len(competitor_urls)} competitors")
        for i, url in enumerate(competitor_urls[:3], 1):
            print(f"  {i}. {url[:60]}...")
        if len(competitor_urls) > 3:
            print(f"  ... and {len(competitor_urls) - 3} more")
        
        # Step 2: Scrape target URL
        print("\n[3/7] Scraping 500rockets.io...")
        target_data = await scraping_service.scrape_url(target_url)
        
        if target_data.get("error"):
            print(f"✗ Error scraping target: {target_data['error']}")
            return
        
        print(f"✓ Scraped 500rockets.io")
        print(f"  - Title: {target_data.get('title', 'N/A')[:60]}")
        print(f"  - Content: {len(target_data.get('main_content', ''))} chars")
        print(f"  - H-tags: {len(target_data.get('h_tags', []))}")
        
        # Step 3: Scrape top 3 competitors (for speed)
        print("\n[4/7] Scraping top 3 competitors...")
        competitor_data = []
        for i, url in enumerate(competitor_urls[:3], 1):
            print(f"  Scraping competitor {i}/3...")
            try:
                data = await scraping_service.scrape_url(url)
                if not data.get("error"):
                    competitor_data.append((url, data))
                    print(f"    ✓ {url[:50]}...")
            except Exception as e:
                print(f"    ✗ Failed: {str(e)[:50]}")
        
        print(f"✓ Scraped {len(competitor_data)} competitors")
        
        # Step 4: Score 500rockets.io
        print("\n[5/7] Scoring 500rockets.io (8 dimensions)...")
        target_score = await scoring_service.generate_content_score(
            query=query,
            title=target_data.get('title', ''),
            description=target_data.get('description', ''),
            content=target_data.get('main_content', ''),
            h_tags=target_data.get('h_tags', [])
        )
        
        print(f"✓ Scoring complete!")
        print(f"\n  📊 500ROCKETS.IO SCORES:")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  1. Metadata Alignment:         {target_score.metadata_alignment:.1f}/100")
        print(f"  2. Hierarchical Decomposition: {target_score.hierarchical_decomposition:.1f}/100")
        print(f"  3. Thematic Unity:             {target_score.thematic_unity:.1f}/100")
        print(f"  4. Balance:                    {target_score.balance:.1f}/100")
        print(f"  5. Query Intent:               {target_score.query_intent:.1f}/100")
        print(f"  6. Structural Coherence:       {target_score.structural_coherence:.1f}/100")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  7. Composite Score:            {target_score.composite_score:.1f}/100")
        print(f"  8. SEO Score:                  {target_score.seo_score:.1f}/100")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Step 5: Score competitors
        print("\n[6/7] Scoring competitors...")
        competitor_scores = []
        for url, data in competitor_data:
            try:
                score = await scoring_service.generate_content_score(
                    query=query,
                    title=data.get('title', ''),
                    description=data.get('description', ''),
                    content=data.get('main_content', ''),
                    h_tags=data.get('h_tags', [])
                )
                competitor_scores.append((url, score))
            except Exception as e:
                print(f"    ✗ Scoring failed for {url[:40]}: {str(e)[:40]}")
        
        print(f"✓ Scored {len(competitor_scores)} competitors")
        
        # Step 6: Generate insights
        print("\n[7/7] Generating competitive insights...")
        
        if competitor_scores:
            avg_competitor_composite = sum(s[1].composite_score for s in competitor_scores) / len(competitor_scores)
            avg_competitor_seo = sum(s[1].seo_score for s in competitor_scores) / len(competitor_scores)
            
            print(f"\n  📈 COMPETITIVE BENCHMARKING:")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"  Your Composite Score:     {target_score.composite_score:.1f}/100")
            print(f"  Competitor Average:       {avg_competitor_composite:.1f}/100")
            print(f"  Difference:               {target_score.composite_score - avg_competitor_composite:+.1f} points")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"  Your SEO Score:           {target_score.seo_score:.1f}/100")
            print(f"  Competitor Average:       {avg_competitor_seo:.1f}/100")
            print(f"  Difference:               {target_score.seo_score - avg_competitor_seo:+.1f} points")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            # Find top performer
            top_competitor = max(competitor_scores, key=lambda x: x[1].seo_score)
            print(f"\n  🏆 TOP COMPETITOR:")
            print(f"  {top_competitor[0][:60]}")
            print(f"  SEO Score: {top_competitor[1].seo_score:.1f}/100")
            
            # Dimension comparison
            print(f"\n  📊 DIMENSION GAPS (You vs Average):")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            dimensions = [
                ('Metadata Alignment', target_score.metadata_alignment, [s[1].metadata_alignment for s in competitor_scores]),
                ('Hierarchical Decomp', target_score.hierarchical_decomposition, [s[1].hierarchical_decomposition for s in competitor_scores]),
                ('Thematic Unity', target_score.thematic_unity, [s[1].thematic_unity for s in competitor_scores]),
                ('Balance', target_score.balance, [s[1].balance for s in competitor_scores]),
                ('Query Intent', target_score.query_intent, [s[1].query_intent for s in competitor_scores]),
                ('Structural Coherence', target_score.structural_coherence, [s[1].structural_coherence for s in competitor_scores]),
            ]
            
            for name, your_score, comp_scores in dimensions:
                avg_comp = sum(comp_scores) / len(comp_scores)
                diff = your_score - avg_comp
                indicator = "🟢" if diff > 0 else "🔴" if diff < -2 else "🟡"
                print(f"  {indicator} {name:20s}: {your_score:5.1f} vs {avg_comp:5.1f} ({diff:+.1f})")
        
        print(f"\n  ✅ TOP RECOMMENDATIONS:")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for i, insight in enumerate(target_score.insights[:5], 1):
            print(f"  {i}. {insight}")
        
        print()
        print("=" * 70)
        print("  ✅ ANALYSIS COMPLETE!")
        print("=" * 70)
        print()
        
    except Exception as e:
        print(f"\n✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(analyze_500rockets())

