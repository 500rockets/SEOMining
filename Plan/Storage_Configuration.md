# Storage Configuration & Organization

## Overview
The SEO Mining project generates various types of data that need organized storage. This document describes the configurable storage system that gives you full control over where files are saved.

## Storage Philosophy

1. **User-Controlled Paths**: All storage locations are configurable
2. **Organized by Project/Keyword**: Each analysis gets its own directory
3. **Separation of Concerns**: Raw data vs processed data vs exports
4. **Platform Agnostic**: Works on Windows, Mac, Linux
5. **Archive-Friendly**: Easy to backup, move, or archive completed projects

## Directory Structure

### Default Layout
```
{BASE_DATA_DIR}/
├── projects/
│   └── {project_name}/
│       └── {keyword_slug}/
│           ├── raw/
│           │   ├── metadata.json
│           │   ├── search_results.json
│           │   ├── competitor_1.html
│           │   ├── competitor_1_text.txt
│           │   └── ...
│           ├── processed/
│           │   ├── embeddings.pkl
│           │   ├── similarity_matrix.json
│           │   └── analysis_results.json
│           ├── reports/
│           │   ├── similarity_report.html
│           │   ├── similarity_report.pdf
│           │   ├── wordcloud.png
│           │   └── recommendations.txt
│           └── iterations/
│               ├── iteration_1/
│               ├── iteration_2/
│               └── ...
├── cache/
│   ├── models/
│   │   └── {model_name}/
│   └── proxies/
│       └── health_status.json
├── exports/
│   ├── csv/
│   ├── json/
│   └── excel/
└── archive/
    └── {project_name}_{date}.zip
```

### Configurable Paths

All paths can be customized via environment variables or config file:

```bash
# Base directory - everything goes under here by default
BASE_DATA_DIR=/path/to/your/data

# Or configure each location independently
DATA_RAW_DIR=/path/to/raw/data
DATA_PROCESSED_DIR=/path/to/processed/data
DATA_REPORTS_DIR=/path/to/reports
DATA_EXPORTS_DIR=/path/to/exports
DATA_CACHE_DIR=/path/to/cache
DATA_ARCHIVE_DIR=/path/to/archive

# Project organization
PROJECT_NAME=my_seo_project
KEYWORD_SLUG_SEPARATOR=_
DATE_FORMAT=%Y%m%d_%H%M%S
```

## Path Resolution Logic

### 1. Absolute Paths
If you provide an absolute path, it's used as-is:
```bash
BASE_DATA_DIR=/Users/mattb/Documents/SEO_Data
```

### 2. Relative Paths
Relative to the project root:
```bash
BASE_DATA_DIR=./data  # → {PROJECT_ROOT}/data
```

### 3. Environment Variables
Use environment variables for dynamic paths:
```bash
BASE_DATA_DIR=${HOME}/SEO_Mining_Data
BASE_DATA_DIR=${USERPROFILE}/Documents/SEO_Mining  # Windows
```

### 4. Platform-Specific Defaults
```python
import os
from pathlib import Path

def get_default_data_dir():
    """Get platform-appropriate default data directory"""
    if os.name == 'nt':  # Windows
        return Path(os.environ['USERPROFILE']) / 'Documents' / 'SEO Mining Data'
    else:  # Mac/Linux
        return Path.home() / 'SEO Mining Data'
```

## Project & Keyword Organization

### Project Naming
```python
# Example: E-commerce SEO Campaign
PROJECT_NAME = "ecommerce_seo_2025"

# Results in:
# /data/projects/ecommerce_seo_2025/
```

### Keyword Slugification
```python
# Input: "best running shoes for men"
# Output: "best_running_shoes_for_men"

def slugify_keyword(keyword: str) -> str:
    """Convert keyword to filesystem-safe slug"""
    slug = keyword.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[-\s]+', '_', slug)   # Replace spaces/hyphens with underscore
    return slug[:100]  # Limit length
```

### Timestamped Runs
For repeated analyses of the same keyword:
```
{keyword_slug}/
├── run_20251015_143022/
├── run_20251016_091530/
└── latest/ → symlink to most recent run
```

## Storage Module Design

### Module: `utils/storage.py`

```python
from pathlib import Path
from typing import Optional
import os
import json
from datetime import datetime

class StorageManager:
    """Manage all file storage locations"""
    
    def __init__(self, config: dict):
        self.config = config
        self.base_dir = self._resolve_path(config.get('BASE_DATA_DIR', './data'))
        self.ensure_base_structure()
    
    def _resolve_path(self, path_str: str) -> Path:
        """Resolve path with environment variable expansion"""
        expanded = os.path.expandvars(path_str)
        expanded = os.path.expanduser(expanded)
        return Path(expanded).resolve()
    
    def ensure_base_structure(self):
        """Create base directory structure"""
        dirs = [
            self.base_dir / 'projects',
            self.base_dir / 'cache',
            self.base_dir / 'exports',
            self.base_dir / 'archive'
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def get_project_dir(self, project_name: str, keyword: str, 
                       create: bool = True) -> Path:
        """Get directory for a specific project/keyword"""
        slug = self.slugify_keyword(keyword)
        project_dir = self.base_dir / 'projects' / project_name / slug
        
        if create:
            project_dir.mkdir(parents=True, exist_ok=True)
            
        return project_dir
    
    def get_raw_data_dir(self, project_name: str, keyword: str) -> Path:
        """Get raw data directory"""
        project_dir = self.get_project_dir(project_name, keyword)
        raw_dir = project_dir / 'raw'
        raw_dir.mkdir(parents=True, exist_ok=True)
        return raw_dir
    
    def get_processed_data_dir(self, project_name: str, keyword: str) -> Path:
        """Get processed data directory"""
        project_dir = self.get_project_dir(project_name, keyword)
        processed_dir = project_dir / 'processed'
        processed_dir.mkdir(parents=True, exist_ok=True)
        return processed_dir
    
    def get_reports_dir(self, project_name: str, keyword: str) -> Path:
        """Get reports directory"""
        project_dir = self.get_project_dir(project_name, keyword)
        reports_dir = project_dir / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        return reports_dir
    
    def get_cache_dir(self, cache_type: str = 'general') -> Path:
        """Get cache directory"""
        cache_dir = self.base_dir / 'cache' / cache_type
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def get_export_dir(self, export_format: str = 'csv') -> Path:
        """Get export directory"""
        export_dir = self.base_dir / 'exports' / export_format
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir
    
    def save_raw_html(self, project_name: str, keyword: str, 
                     url: str, html: str, position: int) -> Path:
        """Save raw HTML file"""
        raw_dir = self.get_raw_data_dir(project_name, keyword)
        filename = f"competitor_{position}_{self._url_to_filename(url)}.html"
        file_path = raw_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return file_path
    
    def save_extracted_text(self, project_name: str, keyword: str,
                           url: str, text: str, position: int) -> Path:
        """Save extracted text file"""
        raw_dir = self.get_raw_data_dir(project_name, keyword)
        filename = f"competitor_{position}_{self._url_to_filename(url)}_text.txt"
        file_path = raw_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return file_path
    
    def save_metadata(self, project_name: str, keyword: str, 
                     metadata: dict) -> Path:
        """Save metadata JSON"""
        raw_dir = self.get_raw_data_dir(project_name, keyword)
        file_path = raw_dir / 'metadata.json'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return file_path
    
    def save_embeddings(self, project_name: str, keyword: str,
                       embeddings: any) -> Path:
        """Save embeddings (pickle format)"""
        import pickle
        processed_dir = self.get_processed_data_dir(project_name, keyword)
        file_path = processed_dir / 'embeddings.pkl'
        
        with open(file_path, 'wb') as f:
            pickle.dump(embeddings, f)
        
        return file_path
    
    def save_report(self, project_name: str, keyword: str,
                   report_content: str, report_type: str = 'html') -> Path:
        """Save report file"""
        reports_dir = self.get_reports_dir(project_name, keyword)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.{report_type}"
        file_path = reports_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return file_path
    
    def export_csv(self, data: list, filename: str) -> Path:
        """Export data to CSV"""
        import csv
        export_dir = self.get_export_dir('csv')
        file_path = export_dir / filename
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        return file_path
    
    def list_projects(self) -> list:
        """List all projects"""
        projects_dir = self.base_dir / 'projects'
        return [p.name for p in projects_dir.iterdir() if p.is_dir()]
    
    def list_keywords(self, project_name: str) -> list:
        """List all keywords in a project"""
        project_dir = self.base_dir / 'projects' / project_name
        if not project_dir.exists():
            return []
        return [k.name for k in project_dir.iterdir() if k.is_dir()]
    
    def get_project_summary(self, project_name: str) -> dict:
        """Get summary of project storage"""
        project_dir = self.base_dir / 'projects' / project_name
        if not project_dir.exists():
            return {}
        
        keywords = self.list_keywords(project_name)
        total_size = sum(
            f.stat().st_size 
            for f in project_dir.rglob('*') 
            if f.is_file()
        )
        
        return {
            'project_name': project_name,
            'keywords': keywords,
            'keyword_count': len(keywords),
            'total_size_mb': total_size / (1024 * 1024),
            'path': str(project_dir)
        }
    
    @staticmethod
    def slugify_keyword(keyword: str) -> str:
        """Convert keyword to filesystem-safe slug"""
        import re
        slug = keyword.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '_', slug)
        return slug[:100]
    
    @staticmethod
    def _url_to_filename(url: str) -> str:
        """Convert URL to safe filename"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain.replace('.', '_')[:50]
```

## Configuration Examples

### Example 1: Default (Relative Path)
```bash
# .env
BASE_DATA_DIR=./data
PROJECT_NAME=default_project
```
Results in: `{PROJECT_ROOT}/data/projects/default_project/`

### Example 2: User Documents Folder
```bash
# .env
BASE_DATA_DIR=${HOME}/Documents/SEO_Mining_Data
PROJECT_NAME=client_website_audit
```
Results in: `/Users/mattb/Documents/SEO_Mining_Data/projects/client_website_audit/`

### Example 3: External Drive
```bash
# .env
BASE_DATA_DIR=/Volumes/ExternalDrive/SEO_Projects
PROJECT_NAME=ecommerce_optimization
```
Results in: `/Volumes/ExternalDrive/SEO_Projects/projects/ecommerce_optimization/`

### Example 4: Windows Network Share
```bash
# .env
BASE_DATA_DIR=//NAS/SEO_Data
PROJECT_NAME=campaign_2025
```

### Example 5: Separate Locations for Each Type
```bash
# .env - Advanced configuration
DATA_RAW_DIR=/Volumes/FastSSD/raw_data
DATA_PROCESSED_DIR=/Volumes/FastSSD/processed
DATA_REPORTS_DIR=${HOME}/Documents/SEO_Reports
DATA_CACHE_DIR=/tmp/seo_cache
DATA_EXPORTS_DIR=${HOME}/Desktop/SEO_Exports
```

## Docker Volume Mapping

For containerized deployment, map your chosen directory:

```yaml
# docker-compose.yml
services:
  seomining:
    image: seomining:latest
    volumes:
      # Map your chosen directory to container's data directory
      - /Users/mattb/Documents/SEO_Mining_Data:/app/data
      - ./config:/app/config:ro
    environment:
      - BASE_DATA_DIR=/app/data
      - PROJECT_NAME=my_project
```

## CLI Interface

```bash
# Set storage location at runtime
python main.py analyze \
  --keyword "best running shoes" \
  --project "fitness_blog" \
  --data-dir "/Users/mattb/Documents/SEO_Data"

# Or use environment variable
export BASE_DATA_DIR="/Users/mattb/Documents/SEO_Data"
python main.py analyze --keyword "best running shoes"
```

## Usage Example

```python
from utils.storage import StorageManager
from utils.config import load_config

# Initialize storage manager
config = load_config('.env')
storage = StorageManager(config)

# Analyze keyword
project_name = "fitness_blog"
keyword = "best running shoes for marathon"

# Save raw data
html = fetch_competitor_page(url)
storage.save_raw_html(project_name, keyword, url, html, position=1)

# Save extracted text
text = extract_text(html)
storage.save_extracted_text(project_name, keyword, url, text, position=1)

# Save metadata
metadata = {
    'keyword': keyword,
    'search_date': datetime.now(),
    'competitors': competitor_urls
}
storage.save_metadata(project_name, keyword, metadata)

# Save embeddings
embeddings = generate_embeddings(texts)
storage.save_embeddings(project_name, keyword, embeddings)

# Generate and save report
report_html = generate_report(analysis_results)
report_path = storage.save_report(project_name, keyword, report_html, 'html')

print(f"Report saved to: {report_path}")
print(f"All data in: {storage.get_project_dir(project_name, keyword)}")

# Get project summary
summary = storage.get_project_summary(project_name)
print(f"Project: {summary['project_name']}")
print(f"Keywords analyzed: {summary['keyword_count']}")
print(f"Total size: {summary['total_size_mb']:.2f} MB")
```

## Archive & Backup

### Manual Archive
```python
import shutil

def archive_project(project_name: str, storage: StorageManager) -> Path:
    """Archive entire project"""
    project_dir = storage.base_dir / 'projects' / project_name
    archive_dir = storage.base_dir / 'archive'
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = f"{project_name}_{timestamp}"
    
    archive_path = shutil.make_archive(
        str(archive_dir / archive_name),
        'zip',
        project_dir
    )
    
    return Path(archive_path)
```

### Automated Backup
```bash
# Add to cron/scheduler
0 2 * * * python scripts/backup_projects.py --target /backup/drive
```

## Best Practices

1. **Use Absolute Paths for Production**: Avoid confusion about locations
2. **Separate Fast/Slow Storage**: Raw data on fast SSD, archives on HDD
3. **Regular Backups**: Archive completed projects
4. **Clean Up Old Data**: Set retention policies
5. **Document Your Setup**: Note where data lives in your README
6. **Test Path Resolution**: Verify paths work across platforms
7. **Use Environment Variables**: Keep configuration flexible

## Migration

If you need to move data:

```python
def migrate_storage(old_base: str, new_base: str):
    """Migrate all data to new location"""
    import shutil
    from pathlib import Path
    
    old_path = Path(old_base)
    new_path = Path(new_base)
    
    # Copy directory structure
    shutil.copytree(old_path, new_path, dirs_exist_ok=True)
    
    # Update .env
    update_env_file('BASE_DATA_DIR', str(new_path))
    
    print(f"Migrated from {old_path} to {new_path}")
```

