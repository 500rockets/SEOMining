"""
Manual Content Management System
For handling failed scrapes and manual content input
"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class ManualContentManager:
    """
    Manages manual content input when scraping fails
    Allows you to manually add competitor content for analysis
    """
    
    def __init__(self, content_dir: str = "/app/manual_content"):
        self.content_dir = content_dir
        self.ensure_content_dir()
    
    def ensure_content_dir(self):
        """Create content directory if it doesn't exist"""
        os.makedirs(self.content_dir, exist_ok=True)
        logger.info("content_directory_ready", path=self.content_dir)
    
    def save_manual_content(
        self,
        url: str,
        title: str,
        content: str,
        meta_description: str = "",
        source: str = "manual"
    ) -> str:
        """
        Save manually provided content for analysis
        
        Args:
            url: The URL this content represents
            title: Page title
            content: Full page content
            meta_description: Meta description
            source: How this content was obtained (manual, scrape, etc.)
            
        Returns:
            Path to saved content file
        """
        # Create filename from URL
        filename = self._url_to_filename(url)
        filepath = os.path.join(self.content_dir, f"{filename}.json")
        
        # Prepare content data
        content_data = {
            "url": url,
            "title": title,
            "content": content,
            "meta_description": meta_description,
            "source": source,
            "added_at": datetime.now().isoformat(),
            "content_length": len(content),
            "word_count": len(content.split())
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        logger.info(
            "manual_content_saved",
            url=url,
            filepath=filepath,
            content_length=len(content),
            word_count=len(content.split())
        )
        
        return filepath
    
    def load_manual_content(self, url: str) -> Optional[Dict]:
        """Load manually saved content"""
        filename = self._url_to_filename(url)
        filepath = os.path.join(self.content_dir, f"{filename}.json")
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_manual_content(self) -> List[Dict]:
        """List all manually saved content files"""
        content_files = []
        
        for filename in os.listdir(self.content_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.content_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content_data = json.load(f)
                    content_files.append(content_data)
                except Exception as e:
                    logger.warning("failed_to_load_content_file", filepath=filepath, error=str(e))
        
        return content_files
    
    def _url_to_filename(self, url: str) -> str:
        """Convert URL to safe filename"""
        import re
        # Remove protocol and replace special chars
        filename = url.replace('https://', '').replace('http://', '')
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        filename = filename.replace('__', '_').strip('_')
        return filename[:100]  # Limit length
    
    def get_content_for_analysis(self, urls: List[str]) -> List[Dict]:
        """
        Get content for analysis, preferring manual content over scraping
        
        Args:
            urls: List of URLs to get content for
            
        Returns:
            List of content dictionaries ready for analysis
        """
        content_list = []
        
        for url in urls:
            # First try manual content
            manual_content = self.load_manual_content(url)
            if manual_content:
                content_list.append({
                    'url': url,
                    'content': manual_content['content'],
                    'title': manual_content['title'],
                    'meta_description': manual_content.get('meta_description', ''),
                    'source': 'manual'
                })
                logger.info("using_manual_content", url=url)
            else:
                logger.warning("no_manual_content_found", url=url)
        
        return content_list


def get_manual_content_manager() -> ManualContentManager:
    """Factory function to create ManualContentManager"""
    return ManualContentManager()

