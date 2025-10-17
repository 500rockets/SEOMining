#!/usr/bin/env python
"""
GPU-Intensive Content Generation
Runs for 1 hour using both GPUs to generate complete optimized page content
"""
import sys
sys.path.insert(0, '/app')

import asyncio
import json
from datetime import datetime
from app.services.optimization import get_content_generator


async def run_intensive_generation():
    """
    Run 1-hour intensive GPU analysis to generate complete optimized content
    """
    print("=" * 80)
    print("  GPU-INTENSIVE CONTENT GENERATION")
    print("  Running 1-Hour Analysis with 2x RTX 4000 GPUs")
    print("=" * 80)
    print()
    
    # Load previous analysis to get competitor URLs
    print("[1/5] Loading competitor data...")
    try:
        with open('/app/500rockets_analysis_20251015_182119.json', 'r') as f:
            analysis_data = json.load(f)
        
        competitor_urls = [comp['url'] for comp in analysis_data['competitors']]
        target_url = analysis_data['target_url']
        query = analysis_data['query']
        
        print(f"✓ Target: {target_url}")
        print(f"✓ Query: '{query}'")
        print(f"✓ Competitors: {len(competitor_urls)}")
        
    except Exception as e:
        print(f"✗ Could not load analysis data: {e}")
        return
    
    print()
    
    # Initialize content generator
    print("[2/5] Initializing GPU-accelerated content generator...")
    generator = await get_content_generator()
    print("✓ Content generator ready (2x RTX 4000 GPUs active)")
    print()
    
    # Run intensive generation
    print("[3/5] Starting 60-minute intensive analysis...")
    print("  🔥 This will use both GPUs intensively for maximum optimization")
    print("  📊 Processing thousands of phrases and semantic relationships")
    print("  ⚡ GPU acceleration: ~20x faster than CPU")
    print()
    
    start_time = datetime.now()
    
    result = await generator.generate_optimized_content(
        target_url=target_url,
        query=query,
        competitor_urls=competitor_urls,
        run_duration_minutes=60  # 1 hour intensive analysis
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60
    
    print()
    print(f"✓ Analysis complete! Duration: {duration:.1f} minutes")
    print()
    
    # Display results
    print("=" * 80)
    print("  GENERATION RESULTS")
    print("=" * 80)
    print()
    
    metadata = result['generation_metadata']
    print(f"Analysis Duration: {metadata['analysis_duration_minutes']} minutes")
    print(f"Competitors Analyzed: {metadata['competitors_analyzed']}")
    print(f"Phrases Extracted: {metadata['phrases_extracted']}")
    print(f"Semantic Gaps Found: {metadata['gaps_found']}")
    print(f"Generated At: {metadata['generated_at']}")
    print()
    
    # Show top semantic gaps
    print("=" * 80)
    print("  TOP SEMANTIC GAPS IDENTIFIED")
    print("=" * 80)
    print()
    
    semantic_gaps = result['semantic_insights']['semantic_gaps']
    for i, gap in enumerate(semantic_gaps[:10], 1):
        print(f"{i}. \"{gap['phrase']}\"")
        print(f"   Impact: +{gap['estimated_impact']:.1f} points")
        print(f"   Query Match: {gap['query_similarity']*100:.1f}%")
        print(f"   Used by: {gap['competitor_usage']} competitors")
        print()
    
    # Save optimized content
    print("[4/5] Saving optimized content...")
    
    optimized_content = result['optimized_content']
    
    # Save as markdown file
    with open('/app/optimized_500rockets_content.md', 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    # Save full results
    with open('/app/intensive_generation_results.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    
    print("✓ Optimized content saved to: optimized_500rockets_content.md")
    print("✓ Full results saved to: intensive_generation_results.json")
    print()
    
    # Display content preview
    print("[5/5] Content Preview")
    print("=" * 80)
    print()
    
    # Show first 1000 characters
    preview = optimized_content[:1000] + "..." if len(optimized_content) > 1000 else optimized_content
    print(preview)
    print()
    
    print("=" * 80)
    print("  GENERATION COMPLETE")
    print("=" * 80)
    print()
    print("🎯 Complete optimized page content generated!")
    print("📄 Ready to implement: optimized_500rockets_content.md")
    print("🚀 GPU-intensive analysis: COMPLETE")
    print("⚡ Both RTX 4000 GPUs utilized for maximum optimization")
    print()
    print("Next steps:")
    print("1. Review optimized_500rockets_content.md")
    print("2. Implement the content on your website")
    print("3. Run analysis again to measure improvement")
    print()


if __name__ == "__main__":
    asyncio.run(run_intensive_generation())

