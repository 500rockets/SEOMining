#!/usr/bin/env python3
"""
Semantic Gaps Analysis - Check comprehensiveness
"""

import json
from pathlib import Path

def analyze_semantic_gaps():
    # Load semantic gaps
    with open('./output/500rockets/06_optimization/semantic_gaps.json', 'r') as f:
        gaps = json.load(f)
    
    print("SEMANTIC GAPS ANALYSIS")
    print("=" * 50)
    print(f"Total semantic gaps: {len(gaps)}")
    print()
    
    # Usage analysis
    high_usage = [g for g in gaps if g['competitor_usage_pct'] > 50]
    medium_usage = [g for g in gaps if 25 <= g['competitor_usage_pct'] <= 50]
    low_usage = [g for g in gaps if g['competitor_usage_pct'] < 25]
    
    print("USAGE ANALYSIS:")
    print(f"High usage (>50%): {len(high_usage)} phrases")
    print(f"Medium usage (25-50%): {len(medium_usage)} phrases")
    print(f"Low usage (<25%): {len(low_usage)} phrases")
    print()
    
    # Impact analysis
    high_impact = [g for g in gaps if g['estimated_impact'] > 7]
    medium_impact = [g for g in gaps if 5 <= g['estimated_impact'] <= 7]
    low_impact = [g for g in gaps if g['estimated_impact'] < 5]
    
    print("IMPACT ANALYSIS:")
    print(f"High impact (>7 points): {len(high_impact)} phrases")
    print(f"Medium impact (5-7 points): {len(medium_impact)} phrases")
    print(f"Low impact (<5 points): {len(low_impact)} phrases")
    print()
    
    # Top phrases by impact
    top_by_impact = sorted(gaps, key=lambda x: x['estimated_impact'], reverse=True)[:10]
    print("TOP 10 BY IMPACT:")
    for i, gap in enumerate(top_by_impact, 1):
        print(f"  {i:2d}. {gap['phrase']:<25} (+{gap['estimated_impact']:5.1f} pts, {gap['competitor_usage_pct']:5.0f}% usage)")
    print()
    
    # Top phrases by usage
    top_by_usage = sorted(gaps, key=lambda x: x['competitor_usage_pct'], reverse=True)[:10]
    print("TOP 10 BY USAGE:")
    for i, gap in enumerate(top_by_usage, 1):
        print(f"  {i:2d}. {gap['phrase']:<25} ({gap['competitor_usage_pct']:5.0f}% usage, +{gap['estimated_impact']:5.1f} pts)")
    print()
    
    # Comprehensive analysis
    total_potential = sum(gap['estimated_impact'] for gap in gaps)
    high_priority_potential = sum(gap['estimated_impact'] for gap in gaps if gap['competitor_usage_pct'] > 50)
    medium_priority_potential = sum(gap['estimated_impact'] for gap in gaps if 25 <= gap['competitor_usage_pct'] <= 50)
    
    print("POTENTIAL IMPACT:")
    print(f"Total potential: +{total_potential:.1f} points")
    print(f"High priority (50%+ usage): +{high_priority_potential:.1f} points")
    print(f"Medium priority (25-50% usage): +{medium_priority_potential:.1f} points")
    print()
    
    # Coverage analysis
    print("COVERAGE ANALYSIS:")
    print("Are we comprehensive enough?")
    print(f"YES - We have {len(gaps)} semantic gaps identified")
    print(f"YES - We have {len(high_usage)} high-priority phrases (50%+ usage)")
    print(f"YES - We have {len(high_impact)} high-impact phrases (7+ points)")
    print(f"YES - Total potential improvement: +{total_potential:.1f} points")
    print()
    
    if len(gaps) >= 50:
        print("RECOMMENDATION: YES, we are comprehensive enough!")
        print("   - 50+ semantic gaps is excellent coverage")
        print("   - Good mix of high/medium/low usage phrases")
        print("   - Strong impact potential across all categories")
    else:
        print("RECOMMENDATION: Consider expanding analysis")
        print("   - More competitors might reveal additional gaps")
        print("   - Deeper content analysis could find more phrases")

if __name__ == "__main__":
    analyze_semantic_gaps()
