"""
Scraping Service Package
Web content extraction with proxy rotation and JavaScript rendering
"""
from .service import ScrapingService, get_scraping_service
from .proxy_manager import ProxyManager, load_proxies_from_file

__all__ = [
    'ScrapingService',
    'get_scraping_service',
    'ProxyManager',
    'load_proxies_from_file',
]
