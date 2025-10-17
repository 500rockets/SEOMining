#!/usr/bin/env python3
"""
Content Integration Engine - The Missing Piece
Takes your existing content and tells you EXACTLY what to change
"""

import json
import re
from pathlib import Path
from datetime import datetime
import argparse

class ContentIntegrationEngine:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.output_dir = self.project_dir / "11_content_integration"
        self.output_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load all analysis data"""
        # Load semantic gaps
        with open(self.project_dir / "06_optimization" / "semantic_gaps.json", 'r') as f:
            self.semantic_gaps = json.load(f)
            
        # Load competitive analysis
        with open(self.project_dir / "05_competitive_analysis" / "competitive_analysis.json", 'r') as f:
            self.competitive_analysis = json.load(f)
            
        # Load project config
        with open(self.project_dir / "00_config" / "project_config.json", 'r') as f:
            self.config = json.load(f)
            
        # Load target content (if available)
        try:
            with open(self.project_dir / "03_competitor_content" / "extracted_content" / f"{self.config.get('project_name', '500rockets')}.io_commzone-mtt.json", 'r') as f:
                self.target_content = json.load(f)
        except:
            self.target_content = None
            
    def analyze_target_content_structure(self):
        """Analyze the current target content structure"""
        
        if not self.target_content:
            return {
                "error": "No target content found",
                "suggestions": "Please ensure target content is scraped first"
            }
        
        # Extract content structure
        content_text = self.target_content.get('text', '')
        content_length = len(content_text.split())
        
        # Analyze headings
        headings = {
            "h1": [],
            "h2": [],
            "h3": []
        }
        
        # Simple heading detection (you'd want more sophisticated parsing)
        lines = content_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                headings["h1"].append(line[2:])
            elif line.startswith('## '):
                headings["h2"].append(line[3:])
            elif line.startswith('### '):
                headings["h3"].append(line[4:])
        
        return {
            "content_length": content_length,
            "headings": headings,
            "content_preview": content_text[:500] + "..." if len(content_text) > 500 else content_text
        }
        
    def generate_specific_edit_instructions(self):
        """Generate specific edit instructions for existing content"""
        
        # Get top semantic gaps
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:10]
        
        # Analyze target content
        target_analysis = self.analyze_target_content_structure()
        
        edit_instructions = {
            "high_priority_edits": [],
            "medium_priority_edits": [],
            "low_priority_edits": [],
            "content_expansion_suggestions": []
        }
        
        # High priority edits (high usage, high impact)
        high_usage_gaps = [gap for gap in top_gaps if gap['competitor_usage_pct'] > 50]
        
        for gap in high_usage_gaps:
            edit_instructions["high_priority_edits"].append({
                "phrase": gap['phrase'],
                "impact": gap['estimated_impact'],
                "usage": gap['competitor_usage_pct'],
                "action": f"Add '{gap['phrase']}' to your content",
                "specific_instructions": [
                    f"Add '{gap['phrase']}' to your H1 title",
                    f"Include '{gap['phrase']}' in your introduction paragraph",
                    f"Use '{gap['phrase']}' in at least 2 H2 headings",
                    f"Add '{gap['phrase']}' to your meta description",
                    f"Include '{gap['phrase']}' in your call-to-action"
                ],
                "before_after_examples": [
                    {
                        "before": "High Quality Message Building Guide",
                        "after": f"High Quality Message Building: {gap['phrase'].title()} Guide"
                    },
                    {
                        "before": "Learn how to build effective messages",
                        "after": f"Learn how to build effective {gap['phrase']}"
                    }
                ]
            })
        
        # Medium priority edits
        medium_usage_gaps = [gap for gap in top_gaps if 25 <= gap['competitor_usage_pct'] <= 50]
        
        for gap in medium_usage_gaps:
            edit_instructions["medium_priority_edits"].append({
                "phrase": gap['phrase'],
                "impact": gap['estimated_impact'],
                "usage": gap['competitor_usage_pct'],
                "action": f"Include '{gap['phrase']}' in your content",
                "specific_instructions": [
                    f"Add '{gap['phrase']}' to one H2 heading",
                    f"Include '{gap['phrase']}' in your content body",
                    f"Use '{gap['phrase']}' in internal links"
                ]
            })
        
        # Content expansion suggestions
        edit_instructions["content_expansion_suggestions"] = [
            {
                "section": "Introduction",
                "current_length": "Short",
                "suggestion": "Expand introduction to include more semantic gaps",
                "specific_phrases": [gap['phrase'] for gap in top_gaps[:3]]
            },
            {
                "section": "Framework Section",
                "current_length": "Missing",
                "suggestion": "Add a dedicated framework section",
                "specific_phrases": [gap['phrase'] for gap in high_usage_gaps]
            },
            {
                "section": "Best Practices",
                "current_length": "Missing",
                "suggestion": "Add best practices section",
                "specific_phrases": [gap['phrase'] for gap in medium_usage_gaps[:3]]
            }
        ]
        
        return edit_instructions
        
    def generate_content_optimization_map(self):
        """Generate a map showing where to optimize content"""
        
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:20]
        
        optimization_map = {
            "title_optimization": {
                "current": "High Quality Message Building",
                "suggested": f"High Quality Message Building: {top_gaps[0]['phrase'].title()} Guide",
                "impact": f"+{top_gaps[0]['estimated_impact']:.1f} points",
                "reason": f"{top_gaps[0]['competitor_usage_pct']:.0f}% of competitors use this phrase"
            },
            "meta_description_optimization": {
                "current": "Learn about high quality message building",
                "suggested": f"Learn how to build high quality {top_gaps[0]['phrase']} with our comprehensive guide",
                "impact": f"+{top_gaps[0]['estimated_impact']:.1f} points",
                "reason": "Includes high-impact semantic gap"
            },
            "heading_optimization": {
                "h1": {
                    "current": "High Quality Message Building",
                    "suggested": f"High Quality Message Building: {top_gaps[0]['phrase'].title()} Guide",
                    "impact": f"+{top_gaps[0]['estimated_impact']:.1f} points"
                },
                "h2_suggestions": [
                    f"What is {top_gaps[0]['phrase'].title()}?",
                    f"How to Build {top_gaps[0]['phrase'].title()}",
                    f"{top_gaps[0]['phrase'].title()} Best Practices",
                    f"Common {top_gaps[0]['phrase'].title()} Mistakes"
                ]
            },
            "content_body_optimization": {
                "introduction": {
                    "add_phrases": [gap['phrase'] for gap in top_gaps[:3]],
                    "impact": f"+{sum(gap['estimated_impact'] for gap in top_gaps[:3]):.1f} points"
                },
                "body_sections": {
                    "add_phrases": [gap['phrase'] for gap in top_gaps[3:8]],
                    "impact": f"+{sum(gap['estimated_impact'] for gap in top_gaps[3:8]):.1f} points"
                },
                "conclusion": {
                    "add_phrases": [gap['phrase'] for gap in top_gaps[8:10]],
                    "impact": f"+{sum(gap['estimated_impact'] for gap in top_gaps[8:10]):.1f} points"
                }
            }
        }
        
        return optimization_map
        
    def generate_implementation_roadmap(self):
        """Generate a step-by-step implementation roadmap"""
        
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:10]
        
        roadmap = {
            "phase_1_immediate_changes": {
                "time_required": "30 minutes",
                "expected_impact": f"+{sum(gap['estimated_impact'] for gap in top_gaps[:3]):.1f} points",
                "changes": [
                    {
                        "change": "Update page title",
                        "action": f"Add '{top_gaps[0]['phrase']}' to title",
                        "impact": f"+{top_gaps[0]['estimated_impact']:.1f} points"
                    },
                    {
                        "change": "Update meta description",
                        "action": f"Include '{top_gaps[0]['phrase']}' in description",
                        "impact": f"+{top_gaps[0]['estimated_impact']:.1f} points"
                    },
                    {
                        "change": "Add to H1",
                        "action": f"Include '{top_gaps[0]['phrase']}' in main heading",
                        "impact": f"+{top_gaps[0]['estimated_impact']:.1f} points"
                    }
                ]
            },
            "phase_2_content_expansion": {
                "time_required": "2-3 hours",
                "expected_impact": f"+{sum(gap['estimated_impact'] for gap in top_gaps[3:8]):.1f} points",
                "changes": [
                    {
                        "change": "Add framework section",
                        "action": f"Create section about '{top_gaps[1]['phrase']}'",
                        "impact": f"+{top_gaps[1]['estimated_impact']:.1f} points"
                    },
                    {
                        "change": "Add best practices",
                        "action": f"Include '{top_gaps[2]['phrase']}' best practices",
                        "impact": f"+{top_gaps[2]['estimated_impact']:.1f} points"
                    },
                    {
                        "change": "Expand existing sections",
                        "action": f"Add '{top_gaps[3]['phrase']}' to existing content",
                        "impact": f"+{top_gaps[3]['estimated_impact']:.1f} points"
                    }
                ]
            },
            "phase_3_optimization": {
                "time_required": "1-2 hours",
                "expected_impact": f"+{sum(gap['estimated_impact'] for gap in top_gaps[8:10]):.1f} points",
                "changes": [
                    {
                        "change": "Add internal links",
                        "action": f"Link to other pages using '{top_gaps[8]['phrase']}'",
                        "impact": f"+{top_gaps[8]['estimated_impact']:.1f} points"
                    },
                    {
                        "change": "Optimize CTAs",
                        "action": f"Include '{top_gaps[9]['phrase']}' in call-to-action",
                        "impact": f"+{top_gaps[9]['estimated_impact']:.1f} points"
                    }
                ]
            }
        }
        
        return roadmap
        
    def generate_all_integration_guides(self):
        """Generate all content integration guides"""
        
        print("Generating content integration guides...")
        
        # Generate edit instructions
        edit_instructions = self.generate_specific_edit_instructions()
        
        # Generate optimization map
        optimization_map = self.generate_content_optimization_map()
        
        # Generate implementation roadmap
        roadmap = self.generate_implementation_roadmap()
        
        # Save all guides
        with open(self.output_dir / 'EDIT_INSTRUCTIONS.json', 'w', encoding='utf-8') as f:
            json.dump(edit_instructions, f, indent=2, ensure_ascii=False)
        
        with open(self.output_dir / 'OPTIMIZATION_MAP.json', 'w', encoding='utf-8') as f:
            json.dump(optimization_map, f, indent=2, ensure_ascii=False)
        
        with open(self.output_dir / 'IMPLEMENTATION_ROADMAP.json', 'w', encoding='utf-8') as f:
            json.dump(roadmap, f, indent=2, ensure_ascii=False)
        
        # Generate summary report
        summary_report = f"""# 🎯 CONTENT INTEGRATION GUIDE
## Exact Changes to Make to Your Existing Content

---

## 🚀 IMMEDIATE ACTIONS (30 minutes, +{sum(gap['estimated_impact'] for gap in sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:3]):.1f} points)

### 1. Update Page Title
**Current**: High Quality Message Building
**New**: High Quality Message Building: {sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[0]['phrase'].title()} Guide
**Impact**: +{sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[0]['estimated_impact']:.1f} points

### 2. Update Meta Description
**Current**: Learn about high quality message building
**New**: Learn how to build high quality {sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[0]['phrase']} with our comprehensive guide
**Impact**: +{sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[0]['estimated_impact']:.1f} points

### 3. Update H1 Heading
**Current**: High Quality Message Building
**New**: High Quality Message Building: {sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[0]['phrase'].title()} Guide
**Impact**: +{sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[0]['estimated_impact']:.1f} points

---

## 📈 CONTENT EXPANSION (2-3 hours, +{sum(gap['estimated_impact'] for gap in sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[3:8]):.1f} points)

### Add These Sections:
1. **What is {sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[0]['phrase'].title()}?**
2. **How to Build {sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[0]['phrase'].title()}**
3. **{sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[0]['phrase'].title()} Best Practices**

### Add These Phrases to Existing Content:
{chr(10).join([f"- '{gap['phrase']}' (+{gap['estimated_impact']:.1f} points)" for gap in sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[3:8]])}

---

## 🎯 EXPECTED RESULTS
- **Total Impact**: +{sum(gap['estimated_impact'] for gap in sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:10]):.1f} points
- **Ranking Improvement**: Move from "not ranking" to top 10
- **Time Investment**: 3-4 hours total
- **ROI**: High (immediate ranking improvement)

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(self.output_dir / 'INTEGRATION_SUMMARY.md', 'w', encoding='utf-8') as f:
            f.write(summary_report)
        
        print(f"Content integration guides complete: {self.output_dir}")
        print("\nGenerated files:")
        print("   INTEGRATION_SUMMARY.md - Quick action guide")
        print("   EDIT_INSTRUCTIONS.json - Detailed edit instructions")
        print("   OPTIMIZATION_MAP.json - Content optimization map")
        print("   IMPLEMENTATION_ROADMAP.json - Step-by-step roadmap")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate content integration guides')
    parser.add_argument('--project-dir', default='./output/500rockets', 
                       help='Path to project directory')
    
    args = parser.parse_args()
    
    engine = ContentIntegrationEngine(args.project_dir)
    engine.generate_all_integration_guides()
