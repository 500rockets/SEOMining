#!/usr/bin/env python3
"""
Complete Workflow Runner
Processes data through each step of the SEO analysis workflow
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


class WorkflowRunner:
    """Runs the complete SEO analysis workflow"""
    
    def __init__(self, project_name: str = "500rockets"):
        self.project_name = project_name
        self.project_dir = Path(f"/app/projects/{project_name}")
        self.config_file = self.project_dir / "00_config" / "project_config.json"
        
        # Load project config
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def update_status(self, step: str, status: str = "completed"):
        """Update project status"""
        self.config["current_step"] = step
        if step not in self.config["steps_completed"]:
            self.config["steps_completed"].append(step)
        self.config["status"] = status
        self.config["last_updated"] = datetime.now().isoformat()
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
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
        semantic_optimizer = get_semantic_optimizer()
        
        # Process target content
        print("🧠 Processing target content...")
        target_phrases = semantic_optimizer.extract_phrases(target['content'])
        target_embeddings = embedding_service.encode(target_phrases)
        
        # Save target processing results
        target_processing = {
            "url": target['url'],
            "phrases": target_phrases,
            "embeddings": target_embeddings,
            "phrase_count": len(target_phrases),
            "processed_at": datetime.now().isoformat()
        }
        
        processing_dir = self.project_dir / "04_content_processing"
        with open(processing_dir / "target_processing.json", 'w', encoding='utf-8') as f:
            json.dump(target_processing, f, indent=2, ensure_ascii=False)
        
        # Process competitor content
        print("🧠 Processing competitor content...")
        competitor_processing = []
        
        for competitor in competitors:
            phrases = semantic_optimizer.extract_phrases(competitor['content'])
            embeddings = embedding_service.encode(phrases)
            
            competitor_data = {
                "url": competitor['url'],
                "filename": competitor.get('filename', ''),
                "phrases": phrases,
                "embeddings": embeddings,
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
            processing_results["target"]["phrases"],
            processing_results["target"]["url"]
        )
        
        # Score competitors
        print("📊 Scoring competitor content...")
        competitor_scores = []
        
        for competitor in processing_results["competitors"]:
            score = scoring_service.score_content(
                competitor["phrases"],
                competitor["url"]
            )
            
            competitor_scores.append({
                "url": competitor["url"],
                "filename": competitor.get("filename", ""),
                "score": score,
                "phrase_count": competitor["phrase_count"]
            })
        
        # Create competitive analysis
        analysis = {
            "query": self.config["query"],
            "target_url": self.config["target_url"],
            "target_score": target_score,
            "competitors": competitor_scores,
            "analysis_metadata": {
                "total_competitors": len(competitor_scores),
                "analysis_date": datetime.now().isoformat(),
                "project_name": self.project_name
            }
        }
        
        # Save analysis results
        analysis_dir = self.project_dir / "05_competitive_analysis"
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
        semantic_optimizer = get_semantic_optimizer()
        
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
        semantic_gaps = semantic_optimizer.analyze_semantic_gaps(
            target_phrases, phrase_embeddings, query_embedding, phrase_sources
        )
        
        # Sort by estimated impact
        semantic_gaps.sort(key=lambda x: x.get('estimated_points', 0), reverse=True)
        
        # Generate recommendations
        top_gaps = semantic_gaps[:20]
        recommendations = {
            "query": self.config["query"],
            "target_url": self.config["target_url"],
            "total_gaps_found": len(semantic_gaps),
            "top_gaps": top_gaps,
            "estimated_improvement": sum(gap.get('estimated_points', 0) for gap in top_gaps[:10]),
            "recommendations": [
                f"Add '{gap['phrase']}' to improve semantic alignment (estimated +{gap.get('estimated_points', 0):.1f} points)"
                for gap in top_gaps[:10]
            ],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Save optimization results
        optimization_dir = self.project_dir / "06_optimization"
        
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
├── 03_competitor_content/ # Competitor content
├── 04_content_processing/ # Content processing
├── 05_competitive_analysis/ # Competitive analysis
├── 06_optimization/     # Optimization recommendations
├── 07_final_reports/    # Final reports
└── 08_archive/          # Archived data
```

---
*Guide generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(reports_dir / "implementation_guide" / "implementation_guide.md", 'w', encoding='utf-8') as f:
            f.write(implementation_guide)
        
        print("✅ Generated executive summary and implementation guide")
        self.update_status("07_final_reports", "completed")
    
    async def run_complete_workflow(self):
        """Run the complete workflow from step 4 to 7"""
        print("=" * 80)
        print("  COMPLETE SEO ANALYSIS WORKFLOW")
        print("=" * 80)
        print(f"Project: {self.project_name}")
        print(f"Query: {self.config['query']}")
        print(f"Target: {self.config['target_url']}")
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
    """Main function to run the workflow"""
    runner = WorkflowRunner("500rockets")
    await runner.run_complete_workflow()


if __name__ == "__main__":
    asyncio.run(main())
