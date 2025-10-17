#!/usr/bin/env python3
"""
Organized GPU Analysis Script
Uses proper output structure and consistent file naming
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.append('/app')

from app.output_manager import AnalysisOutputManager
from app.services.embeddings import get_embedding_service
from app.services.optimization import get_semantic_optimizer


def load_competitor_data():
    """Load all competitor data from manual_content directory"""
    manual_content_dir = "/app/manual_content"
    competitors = []
    
    if not os.path.exists(manual_content_dir):
        print(f"❌ Manual content directory not found: {manual_content_dir}")
        return []
    
    for filename in os.listdir(manual_content_dir):
        if filename.endswith('.json') and filename != '500rockets.io.json':
            filepath = os.path.join(manual_content_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    competitors.append({
                        'filename': filename,
                        'url': data.get('url', ''),
                        'title': data.get('title', ''),
                        'content': data.get('content', ''),
                        'source': data.get('source', 'manual')
                    })
                print(f"✅ Loaded: {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
    
    return competitors


def load_target_data():
    """Load target data (500rockets.io)"""
    target_file = "/app/manual_content/500rockets.io.json"
    
    if not os.path.exists(target_file):
        print(f"❌ Target file not found: {target_file}")
        return None
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                'url': data.get('url', ''),
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'source': data.get('source', 'manual')
            }
    except Exception as e:
        print(f"❌ Error loading target data: {e}")
        return None


async def run_organized_gpu_analysis():
    """Run GPU analysis with organized output structure"""
    print("=" * 80)
    print("  ORGANIZED GPU SEMANTIC ANALYSIS")
    print("=" * 80)
    print()
    
    # Initialize output manager
    output_manager = AnalysisOutputManager()
    
    # Create project structure
    project_name = "500rockets"
    query = "marketing agency services"
    paths = output_manager.create_project_structure(project_name, query)
    
    print(f"📁 Project: {project_name}")
    print(f"🔍 Query: {query}")
    print(f"📂 Analysis directory: {paths['analysis_dir']}")
    print()
    
    # Load data
    print("📊 Loading competitor and target data...")
    competitors = load_competitor_data()
    target = load_target_data()
    
    if not competitors:
        print("❌ No competitor data found!")
        return
    
    if not target:
        print("❌ No target data found!")
        return
    
    print(f"✅ Loaded {len(competitors)} competitors")
    print(f"✅ Loaded target: {target['url']}")
    print()
    
    # Save raw competitor data
    competitor_data = {
        'target': target,
        'competitors': competitors,
        'query': query,
        'loaded_at': datetime.now().isoformat()
    }
    output_manager.save_competitor_data(paths, competitor_data)
    
    # Initialize services
    print("🚀 Initializing GPU services...")
    embedding_service = get_embedding_service()
    semantic_optimizer = get_semantic_optimizer()
    
    print("✅ Services initialized")
    print()
    
    # Extract phrases from all content
    print("🔍 Extracting phrases from all content...")
    all_phrases = []
    phrase_sources = {}
    
    # Add target phrases
    target_phrases = semantic_optimizer.extract_phrases(target['content'])
    all_phrases.extend(target_phrases)
    for phrase in target_phrases:
        phrase_sources[phrase] = phrase_sources.get(phrase, []) + ['target']
    
    # Add competitor phrases
    for competitor in competitors:
        competitor_phrases = semantic_optimizer.extract_phrases(competitor['content'])
        all_phrases.extend(competitor_phrases)
        for phrase in competitor_phrases:
            phrase_sources[phrase] = phrase_sources.get(phrase, []) + [competitor['filename']]
    
    # Remove duplicates while preserving sources
    unique_phrases = list(set(all_phrases))
    print(f"✅ Extracted {len(unique_phrases)} unique phrases from {len(all_phrases)} total phrases")
    print()
    
    # Generate embeddings
    print("🧠 Generating embeddings with GPU...")
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
    query_embedding = embedding_service.encode([query])[0]
    print("✅ Embeddings generated")
    print()
    
    # Analyze semantic gaps
    print("🎯 Analyzing semantic gaps...")
    semantic_gaps = semantic_optimizer.analyze_semantic_gaps(
        target_phrases, phrase_embeddings, query_embedding, phrase_sources
    )
    
    # Sort by estimated impact
    semantic_gaps.sort(key=lambda x: x.get('estimated_points', 0), reverse=True)
    
    print(f"✅ Found {len(semantic_gaps)} semantic gaps")
    print()
    
    # Generate optimization recommendations
    print("💡 Generating optimization recommendations...")
    top_gaps = semantic_gaps[:20]  # Top 20 gaps
    
    recommendations = {
        'query': query,
        'target_url': target['url'],
        'total_competitors': len(competitors),
        'total_phrases_analyzed': len(unique_phrases),
        'semantic_gaps_found': len(semantic_gaps),
        'top_gaps': top_gaps,
        'estimated_improvement': sum(gap.get('estimated_points', 0) for gap in top_gaps[:10]),
        'recommendations': [
            f"Add '{gap['phrase']}' to improve semantic alignment (estimated +{gap.get('estimated_points', 0):.1f} points)"
            for gap in top_gaps[:10]
        ],
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    print(f"✅ Generated {len(recommendations['recommendations'])} recommendations")
    print()
    
    # Prepare results
    results = {
        'query': query,
        'target_url': target['url'],
        'target_data': target,
        'competitors': competitors,
        'semantic_gaps': semantic_gaps,
        'top_gaps': top_gaps,
        'recommendations': recommendations,
        'analysis_metadata': {
            'total_phrases': len(unique_phrases),
            'total_gaps': len(semantic_gaps),
            'gpu_used': True,
            'analysis_time': datetime.now().isoformat()
        }
    }
    
    # Save all results
    print("💾 Saving results...")
    output_manager.save_analysis_results(paths, results, "gpu_semantic")
    output_manager.save_optimization_recommendations(paths, recommendations)
    output_manager.create_summary_report(paths, results)
    
    print()
    print("=" * 80)
    print("  ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"📊 Total phrases analyzed: {len(unique_phrases)}")
    print(f"🎯 Semantic gaps found: {len(semantic_gaps)}")
    print(f"💡 Top recommendations: {len(top_gaps)}")
    print(f"📈 Estimated improvement: +{recommendations['estimated_improvement']:.1f} points")
    print()
    print("📁 Results saved to:")
    print(f"   📂 {paths['analysis_dir']}")
    print(f"   🔗 Latest: {paths['latest_link']}")
    print()
    print("📋 Key files:")
    print(f"   📊 Full analysis: reports/gpu_semantic_analysis_{paths['timestamp']}.json")
    print(f"   📝 Summary report: reports/summary_report_{paths['timestamp']}.md")
    print(f"   💡 Recommendations: optimizations/optimization_recommendations_{paths['timestamp']}.json")
    print()
    
    return results


if __name__ == "__main__":
    asyncio.run(run_organized_gpu_analysis())
