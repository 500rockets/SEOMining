#!/usr/bin/env python3
"""
Hierarchical Project Manager
Manages parent company projects with multiple sub-projects for URLs and keywords
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.append('/app')


class HierarchicalProjectManager:
    """Manages hierarchical project structure: Company -> URL -> Keyword"""
    
    def __init__(self, base_dir: str = "/app/projects"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_company_project(self, company_name: str, description: str = ""):
        """Create a parent company project"""
        company_dir = self.base_dir / company_name
        company_dir.mkdir(exist_ok=True)
        
        # Create company config
        company_config = {
            "company_name": company_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "sub_projects": [],
            "total_analyses": 0,
            "status": "active"
        }
        
        config_file = company_dir / "company_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(company_config, f, indent=2, ensure_ascii=False)
        
        # Create company README
        readme_content = f"""# {company_name} - SEO Analysis Company

## Company Overview
- **Company**: {company_name}
- **Description**: {description}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: Active

## Project Structure
```
/app/projects/{company_name}/
├── company_config.json          # Company configuration
├── README.md                    # This file
├── sub_projects/                # Individual URL/Keyword analyses
│   ├── homepage_marketing-agency-services/
│   ├── services_digital-marketing/
│   └── blog_seo-tips/
└── reports/                     # Company-wide reports
    ├── competitive_landscape/
    ├── keyword_performance/
    └── recommendations/
```

## Sub-Projects
Each sub-project analyzes a specific URL with a specific keyword:
- **Format**: `{{url_slug}}_{{keyword_slug}}`
- **Example**: `homepage_marketing-agency-services`
- **Example**: `services_digital-marketing`

## Usage
1. Create sub-projects for each URL/Keyword combination
2. Run analyses for each sub-project
3. Generate company-wide reports
4. Track performance across all URLs and keywords

---
*Company project created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        readme_file = company_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Create sub-projects directory
        (company_dir / "sub_projects").mkdir(exist_ok=True)
        (company_dir / "reports").mkdir(exist_ok=True)
        (company_dir / "reports" / "competitive_landscape").mkdir(exist_ok=True)
        (company_dir / "reports" / "keyword_performance").mkdir(exist_ok=True)
        (company_dir / "reports" / "recommendations").mkdir(exist_ok=True)
        
        return {
            "company_dir": str(company_dir),
            "config_file": str(config_file),
            "readme_file": str(readme_file)
        }
    
    def create_sub_project(self, company_name: str, target_url: str, keyword: str, description: str = ""):
        """Create a sub-project for a specific URL/Keyword combination"""
        company_dir = self.base_dir / company_name
        
        if not company_dir.exists():
            raise ValueError(f"Company project '{company_name}' does not exist")
        
        # Create sub-project name
        from urllib.parse import urlparse
        parsed_url = urlparse(target_url)
        url_slug = parsed_url.path.strip('/').replace('/', '_') or 'homepage'
        keyword_slug = keyword.lower().replace(' ', '-').replace('_', '-')
        sub_project_name = f"{url_slug}_{keyword_slug}"
        
        sub_project_dir = company_dir / "sub_projects" / sub_project_name
        sub_project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sub-project structure (same as before)
        config_dir = sub_project_dir / "00_config"
        config_dir.mkdir(exist_ok=True)
        
        # Create all the workflow directories
        directories = [
            "01_target_analysis",
            "02_serp_results",
            "03_competitor_content",
            "04_content_processing",
            "05_competitive_analysis",
            "06_optimization",
            "07_final_reports",
            "08_archive"
        ]
        
        for dir_name in directories:
            dir_path = sub_project_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            
            # Create subdirectories based on the directory
            if dir_name == "01_target_analysis":
                (dir_path / "raw_content").mkdir(exist_ok=True)
                (dir_path / "analysis").mkdir(exist_ok=True)
                (dir_path / "reports").mkdir(exist_ok=True)
            elif dir_name == "02_serp_results":
                (dir_path / "api_responses").mkdir(exist_ok=True)
                (dir_path / "url_lists").mkdir(exist_ok=True)
            elif dir_name == "03_competitor_content":
                (dir_path / "raw_html").mkdir(exist_ok=True)
                (dir_path / "extracted_content").mkdir(exist_ok=True)
                (dir_path / "failed_scrapes").mkdir(exist_ok=True)
            elif dir_name == "04_content_processing":
                (dir_path / "chunked_content").mkdir(exist_ok=True)
                (dir_path / "embeddings").mkdir(exist_ok=True)
                (dir_path / "semantic_analysis").mkdir(exist_ok=True)
            elif dir_name == "05_competitive_analysis":
                (dir_path / "scoring").mkdir(exist_ok=True)
                (dir_path / "comparisons").mkdir(exist_ok=True)
                (dir_path / "insights").mkdir(exist_ok=True)
            elif dir_name == "06_optimization":
                (dir_path / "semantic_gaps").mkdir(exist_ok=True)
                (dir_path / "recommendations").mkdir(exist_ok=True)
                (dir_path / "generated_content").mkdir(exist_ok=True)
            elif dir_name == "07_final_reports":
                (dir_path / "executive_summary").mkdir(exist_ok=True)
                (dir_path / "detailed_analysis").mkdir(exist_ok=True)
                (dir_path / "implementation_guide").mkdir(exist_ok=True)
            elif dir_name == "08_archive":
                (dir_path / "previous_analyses").mkdir(exist_ok=True)
                (dir_path / "backups").mkdir(exist_ok=True)
        
        # Create sub-project config
        sub_project_config = {
            "company_name": company_name,
            "sub_project_name": sub_project_name,
            "target_url": target_url,
            "keyword": keyword,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
            "steps_completed": [],
            "current_step": "00_config",
            "folder_structure": {
                "00_config": str(config_dir),
                "01_target_analysis": str(sub_project_dir / "01_target_analysis"),
                "02_serp_results": str(sub_project_dir / "02_serp_results"),
                "03_competitor_content": str(sub_project_dir / "03_competitor_content"),
                "04_content_processing": str(sub_project_dir / "04_content_processing"),
                "05_competitive_analysis": str(sub_project_dir / "05_competitive_analysis"),
                "06_optimization": str(sub_project_dir / "06_optimization"),
                "07_final_reports": str(sub_project_dir / "07_final_reports"),
                "08_archive": str(sub_project_dir / "08_archive")
            }
        }
        
        config_file = config_dir / "sub_project_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sub_project_config, f, indent=2, ensure_ascii=False)
        
        # Create sub-project README
        readme_content = f"""# {sub_project_name} - SEO Analysis

## Sub-Project Overview
- **Company**: {company_name}
- **Target URL**: {target_url}
- **Keyword**: {keyword}
- **Description**: {description}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: Initialized

## Analysis Workflow
This sub-project will analyze how well `{target_url}` performs for the keyword `{keyword}` compared to competitors.

## Workflow Steps
1. **00_config/** - Project configuration
2. **01_target_analysis/** - Analyze target URL
3. **02_serp_results/** - Get SERP results for keyword
4. **03_competitor_content/** - Scrape competitor content
5. **04_content_processing/** - Process content with embeddings
6. **05_competitive_analysis/** - Competitive analysis and scoring
7. **06_optimization/** - Generate optimization recommendations
8. **07_final_reports/** - Create final reports
9. **08_archive/** - Archive previous analyses

## Usage
Run the analysis workflow for this specific URL/Keyword combination.

---
*Sub-project created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        readme_file = sub_project_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Update company config
        company_config_file = company_dir / "company_config.json"
        with open(company_config_file, 'r', encoding='utf-8') as f:
            company_config = json.load(f)
        
        company_config["sub_projects"].append({
            "name": sub_project_name,
            "target_url": target_url,
            "keyword": keyword,
            "created_at": datetime.now().isoformat(),
            "status": "initialized"
        })
        company_config["total_analyses"] = len(company_config["sub_projects"])
        
        with open(company_config_file, 'w', encoding='utf-8') as f:
            json.dump(company_config, f, indent=2, ensure_ascii=False)
        
        return {
            "sub_project_dir": str(sub_project_dir),
            "config_file": str(config_file),
            "readme_file": str(readme_file),
            "sub_project_name": sub_project_name
        }
    
    def list_companies(self):
        """List all company projects"""
        companies = []
        for company_dir in self.base_dir.iterdir():
            if company_dir.is_dir() and (company_dir / "company_config.json").exists():
                with open(company_dir / "company_config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                companies.append(config)
        return companies
    
    def list_sub_projects(self, company_name: str):
        """List all sub-projects for a company"""
        company_dir = self.base_dir / company_name
        if not company_dir.exists():
            return []
        
        sub_projects = []
        sub_projects_dir = company_dir / "sub_projects"
        if sub_projects_dir.exists():
            for sub_project_dir in sub_projects_dir.iterdir():
                if sub_project_dir.is_dir():
                    config_file = sub_project_dir / "00_config" / "sub_project_config.json"
                    if config_file.exists():
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        sub_projects.append(config)
        return sub_projects


def main():
    """Main configuration interface"""
    print("🏢 Hierarchical SEO Project Manager")
    print()
    
    manager = HierarchicalProjectManager()
    
    while True:
        print("Options:")
        print("1. Create new company project")
        print("2. Create new sub-project (URL/Keyword)")
        print("3. List companies")
        print("4. List sub-projects")
        print("5. Exit")
        print()
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            print()
            company_name = input("Enter company name: ").strip()
            description = input("Enter company description (optional): ").strip()
            
            if company_name:
                result = manager.create_company_project(company_name, description)
                print(f"✅ Company project '{company_name}' created!")
                print(f"📁 Location: {result['company_dir']}")
                print()
        
        elif choice == "2":
            print()
            company_name = input("Enter company name: ").strip()
            target_url = input("Enter target URL: ").strip()
            keyword = input("Enter keyword: ").strip()
            description = input("Enter description (optional): ").strip()
            
            if company_name and target_url and keyword:
                try:
                    result = manager.create_sub_project(company_name, target_url, keyword, description)
                    print(f"✅ Sub-project '{result['sub_project_name']}' created!")
                    print(f"📁 Location: {result['sub_project_dir']}")
                    print()
                except ValueError as e:
                    print(f"❌ Error: {e}")
                    print()
        
        elif choice == "3":
            print()
            companies = manager.list_companies()
            if companies:
                print("Companies:")
                for company in companies:
                    print(f"  - {company['company_name']} ({company['total_analyses']} analyses)")
                print()
            else:
                print("No companies found.")
                print()
        
        elif choice == "4":
            print()
            company_name = input("Enter company name: ").strip()
            if company_name:
                sub_projects = manager.list_sub_projects(company_name)
                if sub_projects:
                    print(f"Sub-projects for {company_name}:")
                    for sub_project in sub_projects:
                        print(f"  - {sub_project['sub_project_name']}")
                        print(f"    URL: {sub_project['target_url']}")
                        print(f"    Keyword: {sub_project['keyword']}")
                        print(f"    Status: {sub_project['status']}")
                        print()
                else:
                    print(f"No sub-projects found for {company_name}.")
                    print()
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid option. Please try again.")
            print()


if __name__ == "__main__":
    main()
