"""
Scraping Service - Content extraction with proxy support
Combines Trafilatura, Playwright, and proxy rotation
"""
import time
from typing import Dict, List, Optional, Tuple
from playwright.sync_api import sync_playwright, Page, Browser
import trafilatura
from trafilatura.settings import use_config
import structlog

from .proxy_manager import ProxyManager
from app.core.config import settings

logger = structlog.get_logger(__name__)


class ScrapingService:
    """
    Comprehensive web scraping service
    Features:
    - Trafilatura for content extraction
    - Playwright for JavaScript rendering
    - Proxy rotation support
    - Retry logic with exponential backoff
    - Rate limiting
    """
    
    def __init__(
        self,
        proxy_manager: Optional[ProxyManager] = None,
        headless: bool = True,
        timeout_ms: int = 45000,
        user_agent: Optional[str] = None
    ):
        """
        Initialize scraping service
        
        Args:
            proxy_manager: ProxyManager instance for proxy rotation
            headless: Run browser in headless mode
            timeout_ms: Page load timeout in milliseconds
            user_agent: Custom user agent string
        """
        self.proxy_manager = proxy_manager
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Configure Trafilatura
        self.trafilatura_config = use_config()
        self.trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")
    
    def fetch_with_playwright(
        self,
        url: str,
        proxy: Optional[str] = None,
        wait_for_selector: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Fetch URL with Playwright (JavaScript rendering)
        
        Args:
            url: URL to fetch
            proxy: Proxy string (optional)
            wait_for_selector: CSS selector to wait for (optional)
            
        Returns:
            Tuple of (html_content, final_url)
        """
        with sync_playwright() as p:
            # Configure browser launch
            launch_options = {"headless": self.headless}
            
            # Parse proxy if provided
            proxy_config = None
            if proxy and self.proxy_manager:
                proxy_config = self.proxy_manager.parse_proxy_for_playwright(proxy)
                if proxy_config:
                    logger.info(
                        "using_proxy",
                        url=url,
                        proxy=proxy_config['server']
                    )
            
            browser = p.chromium.launch(**launch_options)
            
            # Create context with proxy and user agent
            context_options = {"user_agent": self.user_agent}
            if proxy_config:
                context_options["proxy"] = proxy_config
            
            context = browser.new_context(**context_options)
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)
            
            try:
                # Navigate to page
                logger.info("fetching_page", url=url)
                page.goto(url, wait_until="networkidle")
                
                # Wait for specific selector if provided
                if wait_for_selector:
                    page.wait_for_selector(wait_for_selector, timeout=10000)
                
                # Additional wait for dynamic content
                time.sleep(1.0)
                
                html = page.content()
                final_url = page.url
                
                logger.info(
                    "page_fetched",
                    url=url,
                    final_url=final_url,
                    html_length=len(html)
                )
                
                return html, final_url
                
            except Exception as e:
                logger.error(
                    "fetch_failed",
                    url=url,
                    error=str(e)
                )
                raise
            finally:
                context.close()
                browser.close()
    
    def extract_content(
        self,
        html: str,
        url: str,
        include_comments: bool = False,
        include_tables: bool = True,
        include_images: bool = True,
        include_links: bool = True
    ) -> Dict:
        """
        Extract clean content from HTML using Trafilatura
        
        Args:
            html: HTML content
            url: Source URL
            include_comments: Include comment sections
            include_tables: Include table data
            include_images: Include image information
            include_links: Include link information
            
        Returns:
            Dict with extracted content and metadata
        """
        try:
            logger.info("extracting_content", url=url)
            
            # Extract with Trafilatura
            extracted = trafilatura.extract(
                html,
                url=url,
                include_comments=include_comments,
                include_tables=include_tables,
                include_images=include_images,
                include_links=include_links,
                output_format='json',
                config=self.trafilatura_config,
                with_metadata=True
            )
            
            if not extracted:
                logger.warning("extraction_empty", url=url)
                return {'error': 'No content extracted'}
            
            # Parse JSON response
            import json
            content_data = json.loads(extracted) if isinstance(extracted, str) else extracted
            
            logger.info(
                "content_extracted",
                url=url,
                text_length=len(content_data.get('text', '')),
                title=content_data.get('title', 'N/A')
            )
            
            return content_data
            
        except Exception as e:
            logger.error(
                "extraction_failed",
                url=url,
                error=str(e)
            )
            return {'error': str(e)}
    
    def scrape_url(
        self,
        url: str,
        use_proxy: bool = True,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> Dict:
        """
        Scrape URL with retry logic and proxy rotation
        
        Args:
            url: URL to scrape
            use_proxy: Use proxy rotation
            max_retries: Maximum retry attempts
            retry_delay: Base delay between retries (exponential backoff)
            
        Returns:
            Dict with content and metadata
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Get proxy if enabled
                proxy = None
                if use_proxy and self.proxy_manager:
                    proxy = self.proxy_manager.get_next_proxy()
                
                # Fetch page with Playwright
                html, final_url = self.fetch_with_playwright(url, proxy)
                
                # Extract content with Trafilatura
                content = self.extract_content(html, final_url)
                
                # Add scraping metadata
                content['scraping_metadata'] = {
                    'original_url': url,
                    'final_url': final_url,
                    'proxy_used': bool(proxy),
                    'attempt': attempt + 1,
                    'html_length': len(html)
                }
                
                return content
                
            except Exception as e:
                last_error = e
                logger.warning(
                    "scrape_attempt_failed",
                    url=url,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e)
                )
                
                # Mark proxy as failed if we used one
                if proxy and self.proxy_manager:
                    self.proxy_manager.mark_proxy_failed(proxy)
                
                # Exponential backoff
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    logger.info("retrying_after_delay", delay=delay)
                    time.sleep(delay)
        
        # All retries failed
        logger.error(
            "scrape_failed_all_retries",
            url=url,
            retries=max_retries,
            last_error=str(last_error)
        )
        
        return {
            'error': f'Failed after {max_retries} attempts',
            'last_error': str(last_error),
            'url': url
        }
    
    def scrape_urls_batch(
        self,
        urls: List[str],
        use_proxy: bool = True,
        delay_between_requests: float = 2.0
    ) -> List[Dict]:
        """
        Scrape multiple URLs with rate limiting
        
        Args:
            urls: List of URLs to scrape
            use_proxy: Use proxy rotation
            delay_between_requests: Delay between requests (seconds)
            
        Returns:
            List of content dicts
        """
        results = []
        
        logger.info("batch_scrape_started", url_count=len(urls))
        
        for i, url in enumerate(urls):
            logger.info(
                "scraping_url",
                index=i + 1,
                total=len(urls),
                url=url
            )
            
            result = self.scrape_url(url, use_proxy=use_proxy)
            results.append(result)
            
            # Rate limiting
            if i < len(urls) - 1:
                time.sleep(delay_between_requests)
        
        logger.info(
            "batch_scrape_complete",
            total=len(urls),
            successful=sum(1 for r in results if 'error' not in r),
            failed=sum(1 for r in results if 'error' in r)
        )
        
        return results
    
    def extract_metadata_only(self, html: str, url: str) -> Dict:
        """
        Extract only metadata without full content
        Faster for quick page analysis
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dict with metadata
        """
        try:
            metadata = trafilatura.extract_metadata(html, default_url=url)
            
            if metadata:
                return {
                    'title': metadata.title,
                    'author': metadata.author,
                    'description': metadata.description,
                    'sitename': metadata.sitename,
                    'date': metadata.date,
                    'url': metadata.url,
                    'categories': metadata.categories,
                    'tags': metadata.tags,
                    'language': metadata.language
                }
            
            return {'error': 'No metadata extracted'}
            
        except Exception as e:
            logger.error(
                "metadata_extraction_failed",
                url=url,
                error=str(e)
            )
            return {'error': str(e)}


# Singleton instance
_scraping_service_instance = None


def get_scraping_service(
    proxy_file: Optional[str] = None,
    headless: bool = True
) -> ScrapingService:
    """
    Get or create singleton scraping service instance
    
    Args:
        proxy_file: Path to proxy file (only used on first call)
        headless: Run browser in headless mode
        
    Returns:
        ScrapingService instance
    """
    global _scraping_service_instance
    
    if _scraping_service_instance is None:
        proxy_manager = None
        if proxy_file:
            proxy_manager = ProxyManager(proxy_file=proxy_file)
        
        _scraping_service_instance = ScrapingService(
            proxy_manager=proxy_manager,
            headless=headless
        )
    
    return _scraping_service_instance

