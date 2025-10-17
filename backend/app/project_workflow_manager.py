#!/usr/bin/env python3
"""
Complete Project Workflow Structure
Organizes the entire SEO analysis process from start to finish
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ProjectWorkflowManager:
    """Manages complete project workflow with organized folder structure"""
    
    def __init__(self, base_dir: str = "/app/projects"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_project_structure(self, project_name: str, query: str, target_url: str) -> Dict:
        """
        Create complete project workflow structure
        
        Args:
            project_name: Name of the project (e.g., "500rockets")
            query: Search query used
            target_url: Target website URL
            
        Returns:
            Dict with all the paths
        """
        # Create timestamp for this project
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create project structure
        project_dir = self.base_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Step 0: Project Configuration
        config_dir = project_dir / "00_config"
        config_dir.mkdir(exist_ok=True)
        
        # Step 1: Target Analysis
        target_dir = project_dir / "01_target_analysis"
        target_dir.mkdir(exist_ok=True)
        (target_dir / "raw_content").mkdir(exist_ok=True)
        (target_dir / "analysis").mkdir(exist_ok=True)
        (target_dir / "reports").mkdir(exist_ok=True)
        
        # Step 2: SERP Results
        serp_dir = project_dir / "02_serp_results"
        serp_dir.mkdir(exist_ok=True)
        (serp_dir / "api_responses").mkdir(exist_ok=True)
        (serp_dir / "url_lists").mkdir(exist_ok=True)
        
        # Step 3: Competitor Scraping
        competitors_dir = project_dir / "03_competitor_content"
        competitors_dir.mkdir(exist_ok=True)
        (competitors_dir / "raw_html").mkdir(exist_ok=True)
        (competitors_dir / "extracted_content").mkdir(exist_ok=True)
        (competitors_dir / "failed_scrapes").mkdir(exist_ok=True)
        
        # Step 4: Content Processing
        processing_dir = project_dir / "04_content_processing"
        processing_dir.mkdir(exist_ok=True)
        (processing_dir / "chunked_content").mkdir(exist_ok=True)
        (processing_dir / "embeddings").mkdir(exist_ok=True)
        (processing_dir / "semantic_analysis").mkdir(exist_ok=True)
        
        # Step 5: Competitive Analysis
        analysis_dir = project_dir / "05_competitive_analysis"
        analysis_dir.mkdir(exist_ok=True)
        (analysis_dir / "scoring").mkdir(exist_ok=True)
        (analysis_dir / "comparisons").mkdir(exist_ok=True)
        (analysis_dir / "insights").mkdir(exist_ok=True)
        
        # Step 6: Optimization
        optimization_dir = project_dir / "06_optimization"
        optimization_dir.mkdir(exist_ok=True)
        (optimization_dir / "semantic_gaps").mkdir(exist_ok=True)
        (optimization_dir / "recommendations").mkdir(exist_ok=True)
        (optimization_dir / "generated_content").mkdir(exist_ok=True)
        
        # Step 7: Final Reports
        reports_dir = project_dir / "07_final_reports"
        reports_dir.mkdir(exist_ok=True)
        (reports_dir / "executive_summary").mkdir(exist_ok=True)
        (reports_dir / "detailed_analysis").mkdir(exist_ok=True)
        (reports_dir / "implementation_guide").mkdir(exist_ok=True)
        
        # Step 8: Archive
        archive_dir = project_dir / "08_archive"
        archive_dir.mkdir(exist_ok=True)
        (archive_dir / "previous_analyses").mkdir(exist_ok=True)
        (archive_dir / "backups").mkdir(exist_ok=True)
        
        # Create project config file
        config_data = {
            "project_name": project_name,
            "query": query,
            "target_url": target_url,
            "created_at": datetime.now().isoformat(),
            "timestamp": timestamp,
            "status": "initialized",
            "steps_completed": [],
            "current_step": "00_config",
            "folder_structure": {
                "00_config": str(config_dir),
                "01_target_analysis": str(target_dir),
                "02_serp_results": str(serp_dir),
                "03_competitor_content": str(competitors_dir),
                "04_content_processing": str(processing_dir),
                "05_competitive_analysis": str(analysis_dir),
                "06_optimization": str(optimization_dir),
                "07_final_reports": str(reports_dir),
                "08_archive": str(archive_dir)
            }
        }
        
        config_file = config_dir / "project_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        # Create README for project
        readme_content = f"""# {project_name} - SEO Analysis Project

## Project Overview
- **Query**: {query}
- **Target URL**: {target_url}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: Initialized

## Workflow Steps

### 00_config/
Project configuration and settings

### 01_target_analysis/
Analysis of the target website
- `raw_content/` - Original HTML and content
- `analysis/` - Target website analysis results
- `reports/` - Target analysis reports

### 02_serp_results/
Search engine results from SERP API
- `api_responses/` - Raw API responses
- `url_lists/` - Processed URL lists

### 03_competitor_content/
Competitor content collection
- `raw_html/` - Original HTML files
- `extracted_content/` - Clean extracted content
- `failed_scrapes/` - Failed scraping attempts

### 04_content_processing/
Content processing and preparation
- `chunked_content/` - Content broken into chunks
- `embeddings/` - Generated embeddings
- `semantic_analysis/` - Semantic analysis results

### 05_competitive_analysis/
Competitive analysis and scoring
- `scoring/` - Individual competitor scores
- `comparisons/` - Comparative analysis
- `insights/` - Key insights and findings

### 06_optimization/
Optimization recommendations
- `semantic_gaps/` - Identified semantic gaps
- `recommendations/` - Optimization recommendations
- `generated_content/` - AI-generated optimized content

### 07_final_reports/
Final reports and deliverables
- `executive_summary/` - High-level summary
- `detailed_analysis/` - Detailed analysis reports
- `implementation_guide/` - Implementation instructions

### 08_archive/
Archived data and backups
- `previous_analyses/` - Historical analyses
- `backups/` - Data backups

## Usage
Each step builds on the previous one. Follow the numerical order for complete analysis.
"""
        
        readme_file = project_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return {
            "project_dir": str(project_dir),
            "config_file": str(config_file),
            "readme_file": str(readme_file),
            "timestamp": timestamp,
            "config_data": config_data,
            "folders": {
                "00_config": str(config_dir),
                "01_target_analysis": str(target_dir),
                "02_serp_results": str(serp_dir),
                "03_competitor_content": str(competitors_dir),
                "04_content_processing": str(processing_dir),
                "05_competitive_analysis": str(analysis_dir),
                "06_optimization": str(optimization_dir),
                "07_final_reports": str(reports_dir),
                "08_archive": str(archive_dir)
            }
        }
    
    def organize_existing_data(self, project_name: str, query: str, target_url: str):
        """Organize existing data into the new workflow structure"""
        print(f"🔄 Organizing existing data for project: {project_name}")
        
        # Create project structure
        structure = self.create_project_structure(project_name, query, target_url)
        
        # Move existing data
        existing_data = {
            "manual_content": "/app/manual_content",
            "old_output": "/app/output",
            "old_analysis": "/app/app/500rockets_analysis_20251015_182119.json"
        }
        
        moved_files = []
        
        # Move manual content to competitor content
        if os.path.exists(existing_data["manual_content"]):
            competitors_dir = structure["folders"]["03_competitor_content"]
            extracted_dir = Path(competitors_dir) / "extracted_content"
            
            for filename in os.listdir(existing_data["manual_content"]):
                if filename.endswith('.json'):
                    src = os.path.join(existing_data["manual_content"], filename)
                    dst = extracted_dir / filename
                    
                    shutil.copy2(src, dst)
                    moved_files.append(f"✅ Moved {filename} → 03_competitor_content/extracted_content/")
        
        # Move old analysis to archive
        if os.path.exists(existing_data["old_analysis"]):
            archive_dir = structure["folders"]["08_archive"]
            previous_dir = Path(archive_dir) / "previous_analyses"
            
            dst = previous_dir / "original_analysis_20251015_182119.json"
            shutil.copy2(existing_data["old_analysis"], dst)
            moved_files.append(f"✅ Archived original analysis → 08_archive/previous_analyses/")
        
        # Update project status
        config_file = structure["config_file"]
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        config_data["status"] = "data_organized"
        config_data["steps_completed"] = ["00_config", "03_competitor_content"]
        config_data["current_step"] = "04_content_processing"
        config_data["moved_files"] = moved_files
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Project structure created: {structure['project_dir']}")
        print(f"📁 Config file: {structure['config_file']}")
        print(f"📖 README: {structure['readme_file']}")
        
        return structure


def create_500rockets_project():
    """Create the 500rockets project with complete workflow structure"""
    print("=" * 80)
    print("  CREATING 500ROCKETS PROJECT WORKFLOW")
    print("=" * 80)
    print()
    
    manager = ProjectWorkflowManager()
    
    structure = manager.organize_existing_data(
        project_name="500rockets",
        query="marketing agency services",
        target_url="https://500rockets.io"
    )
    
    print()
    print("=" * 80)
    print("  PROJECT CREATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("📁 Project location: /app/projects/500rockets/")
    print("📋 Next steps:")
    print("   1. Review project structure in 00_config/")
    print("   2. Run content processing: 04_content_processing/")
    print("   3. Execute competitive analysis: 05_competitive_analysis/")
    print("   4. Generate optimizations: 06_optimization/")
    print("   5. Create final reports: 07_final_reports/")
    print()
    print("🔗 Quick access:")
    print("   docker exec seo-mining-backend ls -la /app/projects/500rockets/")
    print("   docker exec seo-mining-backend cat /app/projects/500rockets/README.md")
    print()
    
    return structure


if __name__ == "__main__":
    create_500rockets_project()
