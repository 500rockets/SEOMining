#!/usr/bin/env python3
"""
Organized Output Structure for SEO Analysis
Creates consistent project-based folder structure and file naming
"""
import os
import json
from datetime import datetime
from pathlib import Path


class AnalysisOutputManager:
    """Manages organized output structure for SEO analysis projects"""
    
    def __init__(self, base_dir: str = "/app/output"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_project_structure(self, project_name: str, query: str) -> dict:
        """
        Create organized folder structure for a project
        
        Args:
            project_name: Name of the project (e.g., "500rockets")
            query: Search query used
            
        Returns:
            Dict with all the paths
        """
        # Create timestamp for this analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create project structure
        project_dir = self.base_dir / project_name
        analysis_dir = project_dir / f"analysis_{timestamp}"
        
        # Create subdirectories
        analysis_dir.mkdir(parents=True, exist_ok=True)
        (analysis_dir / "raw_data").mkdir(exist_ok=True)
        (analysis_dir / "reports").mkdir(exist_ok=True)
        (analysis_dir / "optimizations").mkdir(exist_ok=True)
        (analysis_dir / "content").mkdir(exist_ok=True)
        
        # Create symlink to latest analysis
        latest_link = project_dir / "latest"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(analysis_dir.name)
        
        return {
            "project_dir": str(project_dir),
            "analysis_dir": str(analysis_dir),
            "raw_data_dir": str(analysis_dir / "raw_data"),
            "reports_dir": str(analysis_dir / "reports"),
            "optimizations_dir": str(analysis_dir / "optimizations"),
            "content_dir": str(analysis_dir / "content"),
            "latest_link": str(latest_link),
            "timestamp": timestamp,
            "project_name": project_name,
            "query": query
        }
    
    def save_analysis_results(self, paths: dict, results: dict, analysis_type: str = "gpu_semantic") -> str:
        """
        Save analysis results with proper naming
        
        Args:
            paths: Path structure from create_project_structure
            results: Analysis results to save
            analysis_type: Type of analysis (gpu_semantic, competitive, etc.)
            
        Returns:
            Path to saved file
        """
        # Create filename
        filename = f"{analysis_type}_analysis_{paths['timestamp']}.json"
        filepath = os.path.join(paths["reports_dir"], filename)
        
        # Add metadata
        results_with_metadata = {
            "metadata": {
                "project_name": paths["project_name"],
                "query": paths["query"],
                "analysis_type": analysis_type,
                "timestamp": paths["timestamp"],
                "created_at": datetime.now().isoformat(),
                "filepath": filepath
            },
            "results": results
        }
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_with_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analysis results saved to: {filepath}")
        return filepath
    
    def save_optimization_recommendations(self, paths: dict, recommendations: dict) -> str:
        """Save optimization recommendations"""
        filename = f"optimization_recommendations_{paths['timestamp']}.json"
        filepath = os.path.join(paths["optimizations_dir"], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Optimization recommendations saved to: {filepath}")
        return filepath
    
    def save_generated_content(self, paths: dict, content: str, content_type: str = "optimized") -> str:
        """Save generated content"""
        filename = f"{content_type}_content_{paths['timestamp']}.md"
        filepath = os.path.join(paths["content_dir"], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Generated content saved to: {filepath}")
        return filepath
    
    def save_competitor_data(self, paths: dict, competitor_data: list) -> str:
        """Save raw competitor data"""
        filename = f"competitor_data_{paths['timestamp']}.json"
        filepath = os.path.join(paths["raw_data_dir"], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(competitor_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Competitor data saved to: {filepath}")
        return filepath
    
    def create_summary_report(self, paths: dict, results: dict) -> str:
        """Create a human-readable summary report"""
        filename = f"summary_report_{paths['timestamp']}.md"
        filepath = os.path.join(paths["reports_dir"], filename)
        
        # Extract key metrics
        metadata = results.get("metadata", {})
        analysis_results = results.get("results", {})
        
        # Create markdown report
        report = f"""# SEO Analysis Report

## Project: {metadata.get('project_name', 'Unknown')}
## Query: {metadata.get('query', 'Unknown')}
## Analysis Type: {metadata.get('analysis_type', 'Unknown')}
## Date: {metadata.get('created_at', 'Unknown')}

## Key Findings

### Target Performance
- **Target URL**: {analysis_results.get('target_url', 'N/A')}
- **Composite Score**: {analysis_results.get('target_score', {}).get('composite_score', 'N/A')}
- **SEO Score**: {analysis_results.get('target_score', {}).get('seo_score', 'N/A')}

### Competitive Landscape
- **Total Competitors Analyzed**: {len(analysis_results.get('competitors', []))}
- **Average Competitor Score**: {analysis_results.get('insights', {}).get('average_competitor_score', 'N/A')}
- **Top Competitor Score**: {analysis_results.get('insights', {}).get('top_competitor_score', 'N/A')}

### Semantic Gaps Identified
"""
        
        # Add semantic gaps if available
        semantic_gaps = analysis_results.get('semantic_gaps', [])
        if semantic_gaps:
            report += f"- **Total Gaps Found**: {len(semantic_gaps)}\n\n"
            for i, gap in enumerate(semantic_gaps[:10], 1):  # Top 10
                report += f"{i}. **{gap.get('phrase', 'N/A')}** - Impact: {gap.get('estimated_points', 'N/A')} points\n"
        else:
            report += "- No semantic gaps data available\n"
        
        report += f"""
## Recommendations

### Immediate Actions
1. Review semantic gaps and implement high-impact phrases
2. Analyze top-performing competitors for content structure
3. Optimize metadata alignment based on competitor analysis

### Files Generated
- **Full Analysis**: `{os.path.basename(paths['reports_dir'])}/gpu_semantic_analysis_{paths['timestamp']}.json`
- **Optimization Recommendations**: `{os.path.basename(paths['optimizations_dir'])}/optimization_recommendations_{paths['timestamp']}.json`
- **Raw Competitor Data**: `{os.path.basename(paths['raw_data_dir'])}/competitor_data_{paths['timestamp']}.json`

## Next Steps
1. Review the detailed analysis results
2. Implement optimization recommendations
3. Monitor performance improvements
4. Schedule follow-up analysis

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Summary report saved to: {filepath}")
        return filepath


def organize_existing_results():
    """Move existing results to organized structure"""
    output_manager = AnalysisOutputManager()
    
    # Check for existing results
    existing_files = [
        "/app/working_gpu_analysis_results.json",
        "/app/500rockets_analysis_20251015_182119.json"
    ]
    
    for filepath in existing_files:
        if os.path.exists(filepath):
            print(f"📁 Organizing existing file: {filepath}")
            
            # Load existing results
            with open(filepath, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            # Determine project name and query
            if "500rockets" in filepath:
                project_name = "500rockets"
                query = results.get("query", "marketing agency services")
            else:
                project_name = "default_project"
                query = results.get("query", "unknown query")
            
            # Create organized structure
            paths = output_manager.create_project_structure(project_name, query)
            
            # Save organized results
            output_manager.save_analysis_results(paths, results, "gpu_semantic")
            
            # Create summary report
            output_manager.create_summary_report(paths, {"metadata": {"project_name": project_name, "query": query}, "results": results})
            
            print(f"✅ Organized: {filepath} → {paths['analysis_dir']}")


if __name__ == "__main__":
    print("=" * 60)
    print("  ORGANIZING EXISTING RESULTS")
    print("=" * 60)
    print()
    
    organize_existing_results()
    
    print()
    print("=" * 60)
    print("  ORGANIZATION COMPLETE")
    print("=" * 60)
    print()
    print("📁 New structure created in /app/output/")
    print("🔗 Latest analysis linked in each project folder")
    print("📊 Summary reports generated for easy reading")
    print()
