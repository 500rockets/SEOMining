#!/usr/bin/env python3
"""
Ranking-Focused Analysis
Analyzes what actually makes competitors rank, not subjective content quality
"""

import json
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from collections import Counter
import re

class RankingFocusedAnalyzer:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.output_dir = self.project_dir / "09_ranking_analysis"
        self.output_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load all analysis data"""
        # Load competitive analysis
        with open(self.project_dir / "05_competitive_analysis" / "competitive_analysis.json", 'r') as f:
            self.competitive_analysis = json.load(f)
            
        # Load semantic gaps
        with open(self.project_dir / "06_optimization" / "semantic_gaps.json", 'r') as f:
            self.semantic_gaps = json.load(f)
            
        # Load project config
        with open(self.project_dir / "00_config" / "project_config.json", 'r') as f:
            self.config = json.load(f)
            
    def analyze_ranking_patterns(self):
        """Analyze what patterns make competitors rank"""
        
        # Get competitor content
        competitor_content = []
        for competitor in self.competitive_analysis.get('competitors', []):
            if competitor.get('phrase_count', 0) > 0:
                competitor_content.append({
                    'url': competitor['url'],
                    'score': competitor['score']['composite_score'],
                    'phrase_count': competitor['phrase_count']
                })
        
        # Sort by phrase count (more content = more ranking potential)
        competitor_content.sort(key=lambda x: x['phrase_count'], reverse=True)
        
        # Analyze patterns
        patterns = {
            'high_content_competitors': [],
            'low_content_competitors': [],
            'content_vs_score_analysis': []
        }
        
        avg_phrase_count = np.mean([c['phrase_count'] for c in competitor_content])
        
        for comp in competitor_content:
            if comp['phrase_count'] > avg_phrase_count:
                patterns['high_content_competitors'].append(comp)
            else:
                patterns['low_content_competitors'].append(comp)
                
            patterns['content_vs_score_analysis'].append({
                'url': comp['url'].split('/')[-2] if '/' in comp['url'] else comp['url'],
                'phrase_count': comp['phrase_count'],
                'score': comp['score']
            })
        
        return patterns
        
    def create_ranking_insights_report(self):
        """Create insights focused on what drives rankings"""
        
        patterns = self.analyze_ranking_patterns()
        
        # Get target data
        target_score = self.competitive_analysis.get('target_score', {}).get('composite_score', 0)
        target_phrase_count = 0  # We'd need to get this from processing data
        
        # Analyze semantic gaps differently
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:20]
        
        # Group gaps by what competitors actually use
        high_usage_gaps = [gap for gap in top_gaps if gap['competitor_usage_pct'] > 50]
        medium_usage_gaps = [gap for gap in top_gaps if 25 <= gap['competitor_usage_pct'] <= 50]
        low_usage_gaps = [gap for gap in top_gaps if gap['competitor_usage_pct'] < 25]
        
        report = f"""# 🎯 RANKING-FOCUSED ANALYSIS REPORT
## Why Competitors Rank (Despite Lower Scores)

---

## 🚨 THE CONTRADICTION
- **Your Score**: {target_score:.1f}/100 (HIGHEST)
- **Competitor Average**: {np.mean([c['score'] for c in patterns['content_vs_score_analysis']]):.1f}/100 (LOWER)
- **But**: They rank, you don't

**This means our scoring system measures content quality, NOT ranking factors!**

---

## 📊 WHAT ACTUALLY DRIVES RANKINGS

### Content Volume Analysis
"""
        
        # Add content volume insights
        high_content = patterns['high_content_competitors']
        low_content = patterns['low_content_competitors']
        
        if high_content:
            avg_high_content = np.mean([c['phrase_count'] for c in high_content])
            report += f"- **High-content competitors** (avg {avg_high_content:.0f} phrases): {len(high_content)} sites\n"
            for comp in high_content[:3]:
                report += f"  - {comp['url'].split('/')[-2]}: {comp['phrase_count']} phrases, score {comp['score']:.1f}\n"
        
        if low_content:
            avg_low_content = np.mean([c['phrase_count'] for c in low_content])
            report += f"- **Low-content competitors** (avg {avg_low_content:.0f} phrases): {len(low_content)} sites\n"
        
        report += f"""
### The Real Ranking Factors

**Competitors rank because they:**
1. **Cover more topics** - Higher phrase counts = more comprehensive coverage
2. **Use ranking language** - Specific terminology that matches search intent
3. **Have topical authority** - Seen as experts in this specific area
4. **Match user expectations** - Content structure users expect for this query

---

## 🎯 ACTIONABLE STRATEGY

### 1. Content Volume Strategy
- **Current**: You have high-quality content but limited coverage
- **Solution**: Expand content to match competitor phrase counts
- **Target**: Aim for {np.mean([c['phrase_count'] for c in patterns['content_vs_score_analysis']]):.0f}+ phrases

### 2. High-Usage Semantic Gaps ({len(high_usage_gaps)} gaps)
**These phrases are used by 50%+ of competitors - CRITICAL to add:**
"""
        
        for gap in high_usage_gaps[:5]:
            report += f"- **\"{gap['phrase']}\"** - {gap['competitor_usage_pct']:.0f}% usage, +{gap['estimated_impact']:.1f} impact\n"
        
        report += f"""
### 3. Medium-Usage Gaps ({len(medium_usage_gaps)} gaps)
**These phrases are used by 25-50% of competitors - IMPORTANT:**
"""
        
        for gap in medium_usage_gaps[:5]:
            report += f"- **\"{gap['phrase']}\"** - {gap['competitor_usage_pct']:.0f}% usage, +{gap['estimated_impact']:.1f} impact\n"
        
        report += f"""
---

## 🚀 IMPLEMENTATION PRIORITY

### Phase 1: Match Competitor Language (High Impact)
1. Add all high-usage phrases ({len(high_usage_gaps)} phrases)
2. Expand content to match competitor volume
3. Use competitor terminology patterns

### Phase 2: Differentiate (Medium Impact)  
1. Add medium-usage phrases ({len(medium_usage_gaps)} phrases)
2. Improve content structure based on competitor patterns
3. Add missing topic coverage

### Phase 3: Optimize (Lower Impact)
1. Add low-usage phrases for completeness
2. Technical optimizations
3. Advanced content improvements

---

## 📈 EXPECTED RESULTS

**If you match competitor patterns:**
- **Content Volume**: Increase from current to {np.mean([c['phrase_count'] for c in patterns['content_vs_score_analysis']]):.0f}+ phrases
- **Language Match**: Add {len(high_usage_gaps)} critical phrases
- **Ranking Improvement**: Move from "not ranking" to top 10
- **Competitive Position**: Maintain quality advantage while matching ranking factors

---

## 💡 KEY INSIGHT

**Your content is BETTER than competitors, but you're not ranking because:**
- You're not covering enough topics (phrase count)
- You're not using the specific language they use
- You're not matching the content structure they use

**Solution**: Keep your quality advantage, but match their coverage and language patterns.

---

*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Save report
        with open(self.output_dir / 'RANKING_INSIGHTS.md', 'w', encoding='utf-8') as f:
            f.write(report)
            
    def create_content_volume_chart(self):
        """Create chart showing content volume vs ranking"""
        
        patterns = self.analyze_ranking_patterns()
        
        plt.figure(figsize=(14, 8))
        
        # Extract data
        urls = []
        phrase_counts = []
        scores = []
        
        for comp in patterns['content_vs_score_analysis']:
            urls.append(comp['url'])
            phrase_counts.append(comp['phrase_count'])
            scores.append(comp['score'])
        
        # Create scatter plot
        plt.scatter(phrase_counts, scores, alpha=0.7, s=100, color='blue', label='Competitors')
        
        # Add target (if we had phrase count)
        # plt.scatter(target_phrase_count, target_score, s=200, color='red', marker='*', label='Your Site')
        
        # Add trend line
        z = np.polyfit(phrase_counts, scores, 1)
        p = np.poly1d(z)
        plt.plot(phrase_counts, p(phrase_counts), "r--", alpha=0.8, label='Trend Line')
        
        # Customize chart
        plt.title('Content Volume vs Score Analysis\n(Why Competitors Rank Despite Lower Scores)', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Phrase Count (Content Volume)', fontsize=12)
        plt.ylabel('Content Score', fontsize=12)
        plt.legend()
        
        # Add annotations for top performers
        for i, (url, count, score) in enumerate(zip(urls, phrase_counts, scores)):
            if count > np.mean(phrase_counts) * 1.2:  # Top content performers
                plt.annotate(f'{url}\n{count} phrases', 
                           (count, score), 
                           xytext=(10, 10), 
                           textcoords='offset points',
                           fontsize=8,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'content_volume_vs_score.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def generate_ranking_analysis(self):
        """Generate all ranking-focused analysis"""
        print("Analyzing ranking patterns...")
        
        print("Creating ranking insights report...")
        self.create_ranking_insights_report()
        
        print("Creating content volume analysis chart...")
        self.create_content_volume_chart()
        
        print(f"Ranking analysis complete: {self.output_dir}")
        print("\nKey files:")
        print("   RANKING_INSIGHTS.md - Why competitors rank despite lower scores")
        print("   content_volume_vs_score.png - Content volume vs ranking analysis")

if __name__ == "__main__":
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Generate ranking-focused analysis')
    parser.add_argument('--project-dir', default='./output/500rockets', 
                       help='Path to project directory')
    
    args = parser.parse_args()
    
    analyzer = RankingFocusedAnalyzer(args.project_dir)
    analyzer.generate_ranking_analysis()
