#!/usr/bin/env python
"""
Analysis Scaling Calculator
Shows the difference between current analysis and full intensive analysis
"""
import sys
sys.path.insert(0, '/app')

import json


def analyze_scaling_potential():
    """Show the scaling potential of GPU analysis"""
    
    # Load current results
    with open('/app/working_gpu_analysis_results.json', 'r') as f:
        data = json.load(f)
    
    current = data['analysis_metadata']
    
    print("=" * 80)
    print("  GPU ANALYSIS SCALING POTENTIAL")
    print("=" * 80)
    print()
    
    print("CURRENT ANALYSIS (4 competitors):")
    print("-" * 40)
    print(f"  Competitors analyzed: {current['competitors_analyzed']}")
    print(f"  Phrases extracted: {current['phrases_extracted']:,}")
    print(f"  Semantic gaps found: {current['gaps_found']}")
    print(f"  Processing time: {current['duration_minutes']:.2f} minutes")
    print(f"  GPU utilization: 2x RTX 4000")
    print()
    
    print("IF WE ANALYZED ALL 10 COMPETITORS:")
    print("-" * 40)
    estimated_phrases_10 = int(current['phrases_extracted'] * 2.5)
    estimated_gaps_10 = int(current['gaps_found'] * 2.5)
    estimated_time_10 = current['duration_minutes'] * 2.5
    
    print(f"  Competitors analyzed: 10")
    print(f"  Estimated phrases: {estimated_phrases_10:,}")
    print(f"  Estimated gaps: {estimated_gaps_10}")
    print(f"  Estimated time: {estimated_time_10:.2f} minutes")
    print(f"  Additional insights: +{estimated_gaps_10 - current['gaps_found']} phrases")
    print()
    
    print("IF WE RAN 1-HOUR INTENSIVE ANALYSIS:")
    print("-" * 40)
    estimated_phrases_60 = int(current['phrases_extracted'] * 10)
    estimated_gaps_60 = int(current['gaps_found'] * 10)
    
    print(f"  Competitors analyzed: 10+")
    print(f"  Estimated phrases: {estimated_phrases_60:,}")
    print(f"  Estimated gaps: {estimated_gaps_60}")
    print(f"  Processing time: 60 minutes")
    print(f"  Additional insights: +{estimated_gaps_60 - current['gaps_found']} phrases")
    print()
    
    print("WHAT WE'RE MISSING WITH CURRENT ANALYSIS:")
    print("-" * 40)
    print("  • 6 additional competitors worth of phrases")
    print("  • ~125 additional semantic gaps")
    print("  • More comprehensive service coverage")
    print("  • Better competitive intelligence")
    print("  • More precise optimization recommendations")
    print()
    
    print("TOP 10 PHRASES WE FOUND (from 4 competitors):")
    print("-" * 40)
    for i, gap in enumerate(data['semantic_gaps'][:10], 1):
        print(f"  {i}. \"{gap['phrase']}\" (+{gap['estimated_impact']:.1f} points)")
    print()
    
    print("WHAT WE'D FIND WITH FULL ANALYSIS:")
    print("-" * 40)
    print("  • More specific service phrases")
    print("  • Better semantic clustering")
    print("  • More precise impact estimates")
    print("  • Additional optimization opportunities")
    print("  • Better content structure recommendations")
    print()
    
    print("RECOMMENDATION:")
    print("-" * 40)
    print("  Current analysis: Good for quick wins")
    print("  Full 10-competitor analysis: Better insights")
    print("  1-hour intensive analysis: Maximum optimization")
    print()
    print("  Next step: Add remaining 6 competitors manually")
    print("  Then run full GPU analysis for comprehensive results")


if __name__ == "__main__":
    analyze_scaling_potential()

