#!/usr/bin/env python3
"""
SEO Analysis Report Generator - Simple Version
Creates actionable, visual reports from the analysis data without heavy dependencies
"""

import json
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from datetime import datetime
import argparse

class SEOReportGenerator:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.output_dir = self.project_dir / "08_visual_reports"
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
            
        # Load recommendations
        with open(self.project_dir / "06_optimization" / "recommendations.json", 'r') as f:
            self.recommendations = json.load(f)
            
        # Load project config
        with open(self.project_dir / "00_config" / "project_config.json", 'r') as f:
            self.config = json.load(f)
            
    def create_competitive_positioning_chart(self):
        """Create competitive positioning visualization"""
        plt.figure(figsize=(12, 8))
        
        # Extract competitor data
        competitors = []
        scores = []
        
        for competitor in self.competitive_analysis.get('competitors', []):
            competitors.append(competitor['url'].split('/')[-2] if '/' in competitor['url'] else competitor['url'])
            scores.append(competitor['score']['composite_score'])
            
        # Add target
        target_score = self.competitive_analysis.get('target_score', {}).get('composite_score', 0)
        
        # Create bar chart
        all_names = ['Your Site'] + competitors
        all_scores = [target_score] + scores
        
        colors = ['#ff6b6b'] + ['#4ecdc4'] * len(competitors)
        
        bars = plt.bar(range(len(all_names)), all_scores, color=colors, alpha=0.8)
        
        # Customize chart
        plt.title('Competitive Positioning Analysis\n"High Quality Message Building"', fontsize=16, fontweight='bold')
        plt.xlabel('Websites', fontsize=12)
        plt.ylabel('Composite Score', fontsize=12)
        plt.xticks(range(len(all_names)), all_names, rotation=45, ha='right')
        
        # Add value labels on bars
        for i, (bar, score) in enumerate(zip(bars, all_scores)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Add average line
        avg_score = np.mean(all_scores)
        plt.axhline(y=avg_score, color='red', linestyle='--', alpha=0.7, 
                   label=f'Average: {avg_score:.1f}')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'competitive_positioning.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_semantic_gaps_analysis(self):
        """Create semantic gaps visualization"""
        # Top 20 gaps by impact
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:20]
        
        # Create horizontal bar chart
        plt.figure(figsize=(14, 10))
        
        phrases = [gap['phrase'] for gap in top_gaps]
        impacts = [gap['estimated_impact'] for gap in top_gaps]
        
        bars = plt.barh(range(len(phrases)), impacts, color='#ff6b6b', alpha=0.8)
        
        plt.title('Top 20 Semantic Gaps by Impact\nMissing Phrases That Could Boost Your Rankings', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Estimated Impact Score', fontsize=12)
        plt.ylabel('Missing Phrases', fontsize=12)
        
        # Add phrase labels
        plt.yticks(range(len(phrases)), phrases, fontsize=10)
        
        # Add impact values
        for i, (bar, impact) in enumerate(zip(bars, impacts)):
            plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{impact:.1f}', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'semantic_gaps_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_actionable_summary(self):
        """Create a super actionable summary report"""
        
        # Analyze the data
        target_score = self.competitive_analysis.get('target_score', {}).get('composite_score', 0)
        avg_competitor_score = np.mean([c['score']['composite_score'] for c in self.competitive_analysis.get('competitors', [])])
        
        # Top gaps by impact
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:10]
        
        # Group gaps by theme
        themes = {
            'Framework & Structure': [],
            'Quality & Strategy': [],
            'Technical Terms': [],
            'Action Words': []
        }
        
        for gap in top_gaps:
            phrase = gap['phrase'].lower()
            if any(word in phrase for word in ['framework', 'architecture', 'structure', 'model']):
                themes['Framework & Structure'].append(gap)
            elif any(word in phrase for word in ['quality', 'strategy', 'effective', 'successful']):
                themes['Quality & Strategy'].append(gap)
            elif any(word in phrase for word in ['messaging', 'message', 'communication', 'content']):
                themes['Technical Terms'].append(gap)
            else:
                themes['Action Words'].append(gap)
        
        # Generate report
        report = f"""# 🎯 ACTIONABLE SEO ANALYSIS REPORT
## {self.config.get('project_name', '500rockets')} - "{self.config.get('query', 'high quality message building')}"

---

## 📊 CURRENT SITUATION
- **Your Score**: {target_score:.1f}/100
- **Average Competitor**: {avg_competitor_score:.1f}/100
- **Gap**: {avg_competitor_score - target_score:.1f} points behind average
- **Opportunity**: {sum(gap['estimated_impact'] for gap in top_gaps[:10]):.1f} points available from top 10 improvements

---

## 🚀 TOP 3 IMMEDIATE ACTIONS

### 1. Add "Messaging Framework" Content
- **Impact**: +{top_gaps[0]['estimated_impact']:.1f} points
- **Why**: {top_gaps[0]['competitor_usage_pct']:.0f}% of competitors use this phrase
- **Action**: Create a section explaining your messaging framework methodology

### 2. Include "Message Architecture" Terminology  
- **Impact**: +{top_gaps[1]['estimated_impact']:.1f} points
- **Why**: High relevance ({top_gaps[1]['query_relevance']:.1f}%) to search query
- **Action**: Add architecture diagrams and explanations

### 3. Use "Messaging Is" Construction
- **Impact**: +{top_gaps[2]['estimated_impact']:.1f} points  
- **Why**: {top_gaps[2]['competitor_usage_pct']:.0f}% competitor adoption
- **Action**: Rewrite key sentences to use "messaging is..." format

---

## 📈 CONTENT STRATEGY BY THEME

### 🏗️ Framework & Structure ({len(themes['Framework & Structure'])} gaps)
"""
        
        for gap in themes['Framework & Structure'][:3]:
            report += f"- **{gap['phrase']}** (+{gap['estimated_impact']:.1f} pts) - {gap['competitor_usage_pct']:.0f}% of competitors use this\n"
        
        report += f"""
### 🎯 Quality & Strategy ({len(themes['Quality & Strategy'])} gaps)
"""
        
        for gap in themes['Quality & Strategy'][:3]:
            report += f"- **{gap['phrase']}** (+{gap['estimated_impact']:.1f} pts) - {gap['competitor_usage_pct']:.0f}% of competitors use this\n"
        
        report += f"""
### 🔧 Technical Terms ({len(themes['Technical Terms'])} gaps)
"""
        
        for gap in themes['Technical Terms'][:3]:
            report += f"- **{gap['phrase']}** (+{gap['estimated_impact']:.1f} pts) - {gap['competitor_usage_pct']:.0f}% of competitors use this\n"
        
        report += f"""
---

## 💡 SPECIFIC CONTENT RECOMMENDATIONS

### Add These Exact Phrases:
"""
        
        for i, gap in enumerate(top_gaps[:5], 1):
            report += f"{i}. **\"{gap['phrase']}\"** - {gap['competitor_usage_pct']:.0f}% of competitors use this\n"
        
        report += f"""
### Content Structure Improvements:
1. **Add a "Messaging Framework" section** - Explain your methodology
2. **Include "Message Architecture" diagrams** - Visual representations  
3. **Use "messaging is..." constructions** - Match competitor language patterns
4. **Add technical terminology** - Use industry-standard terms
5. **Include quality indicators** - Words like "effective", "successful", "strategic"

---

## 🎯 EXPECTED RESULTS
- **Immediate Impact**: +{sum(gap['estimated_impact'] for gap in top_gaps[:5]):.1f} points from top 5 changes
- **Full Potential**: +{sum(gap['estimated_impact'] for gap in top_gaps):.1f} points from all gaps
- **Ranking Improvement**: Likely move from "not ranking" to top 10

---

## 📋 IMPLEMENTATION CHECKLIST
- [ ] Add "messaging framework" section to main content
- [ ] Include "message architecture" terminology and diagrams  
- [ ] Rewrite key sentences using "messaging is..." format
- [ ] Add technical terms from semantic gaps list
- [ ] Include quality indicators and strategic language
- [ ] Update meta descriptions with missing phrases
- [ ] Add internal links using new terminology
- [ ] Monitor ranking improvements after 2-4 weeks

---

*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Save report
        with open(self.output_dir / 'ACTIONABLE_SUMMARY.md', 'w', encoding='utf-8') as f:
            f.write(report)
            
    def create_content_suggestions(self):
        """Create specific content suggestions"""
        
        # Get top gaps
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:20]
        
        # Create content suggestions
        suggestions = {
            "title_suggestions": [],
            "heading_suggestions": [],
            "content_suggestions": [],
            "meta_description_suggestions": []
        }
        
        # Title suggestions
        suggestions["title_suggestions"] = [
            f"High Quality Message Building: {gap['phrase'].title()} Guide" 
            for gap in top_gaps[:5]
        ]
        
        # Heading suggestions  
        suggestions["heading_suggestions"] = [
            f"How to Build {gap['phrase'].title()}" for gap in top_gaps[:5]
        ] + [
            f"The Complete {gap['phrase'].title()} Framework" for gap in top_gaps[:5]
        ] + [
            f"{gap['phrase'].title()} Best Practices" for gap in top_gaps[:5]
        ]
        
        # Content suggestions
        suggestions["content_suggestions"] = [
            f"Your {gap['phrase']} is crucial for effective communication. Learn how to develop a comprehensive {gap['phrase']} that aligns with your brand values and resonates with your target audience."
            for gap in top_gaps[:3]
        ]
        
        # Meta description suggestions
        suggestions["meta_description_suggestions"] = [
            f"Learn how to build high quality {gap['phrase']} with our comprehensive guide. Discover proven strategies and frameworks for effective messaging."
            for gap in top_gaps[:3]
        ]
        
        # Save suggestions
        with open(self.output_dir / 'content_suggestions.json', 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, indent=2, ensure_ascii=False)
            
    def generate_all_reports(self):
        """Generate all visual and actionable reports"""
        print("Generating actionable SEO reports...")
        
        # Create visualizations
        print("Creating competitive positioning chart...")
        self.create_competitive_positioning_chart()
        
        print("Creating semantic gaps analysis...")
        self.create_semantic_gaps_analysis()
        
        print("Creating actionable summary...")
        self.create_actionable_summary()
        
        print("Creating content suggestions...")
        self.create_content_suggestions()
        
        print(f"All reports generated in: {self.output_dir}")
        print("\nKey files created:")
        print("   ACTIONABLE_SUMMARY.md - Main actionable report")
        print("   competitive_positioning.png - Visual competitive analysis")
        print("   semantic_gaps_analysis.png - Top missing phrases")
        print("   content_suggestions.json - Specific content ideas")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate actionable SEO reports')
    parser.add_argument('--project-dir', default='./output/500rockets', 
                       help='Path to project directory')
    
    args = parser.parse_args()
    
    generator = SEOReportGenerator(args.project_dir)
    generator.generate_all_reports()