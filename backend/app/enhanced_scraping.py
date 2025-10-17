"""
Enhanced Scraping Service
Handles spam protection, CAPTCHAs, and creates manual content files automatically
"""
import asyncio
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import structlog
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import trafilatura
from urllib.parse import urlparse

logger = structlog.get_logger(__name__)


class EnhancedScrapingService:
    """
    Enhanced scraping service that handles spam protection
    and automatically creates manual content files
    """
    
    def __init__(self, proxy_file: Optional[str] = None):
        self.proxy_file = proxy_file
        self.proxies = self._load_proxies() if proxy_file else []
        self.current_proxy_index = 0
        
    def _load_proxies(self) -> List[str]:
        """Load proxies from file"""
        if not self.proxy_file:
            return []
        try:
            with open(self.proxy_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logger.warning("proxy_file_not_found", file=self.proxy_file)
            return []
    
    def _get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    async def scrape_with_enhanced_protection(
        self,
        url: str,
        max_retries: int = 5,
        retry_delay: float = 3.0
    ) -> Dict:
        """
        Enhanced scraping with spam protection handling
        """
        logger.info("enhanced_scraping_starting", url=url)
        
        for attempt in range(max_retries):
            try:
                # Try different strategies
                if attempt == 0:
                    result = await self._scrape_with_stealth(url)
                elif attempt == 1:
                    result = await self._scrape_with_proxy(url)
                elif attempt == 2:
                    result = await self._scrape_with_delays(url)
                elif attempt == 3:
                    result = await self._scrape_with_mobile_ua(url)
                else:
                    result = await self._scrape_with_rotating_proxies(url)
                
                if result and result.get('content') and len(result['content'].strip()) > 100:
                    logger.info("enhanced_scraping_success", url=url, attempt=attempt+1)
                    return result
                
            except Exception as e:
                logger.warning("enhanced_scraping_attempt_failed", 
                             url=url, attempt=attempt+1, error=str(e))
            
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (2 ** attempt))
        
        logger.error("enhanced_scraping_failed", url=url, attempts=max_retries)
        return {
            'url': url,
            'content': '',
            'title': '',
            'meta_description': '',
            'error': 'Failed after all attempts'
        }
    
    async def _scrape_with_stealth(self, url: str) -> Dict:
        """Scrape with stealth mode"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            page = await context.new_page()
            
            # Add stealth scripts
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # Check for common spam protection
                if await self._detect_spam_protection(page):
                    logger.warning("spam_protection_detected", url=url)
                    return None
                
                html = await page.content()
                title = await page.title()
                
                # Extract content
                content = trafilatura.extract(html)
                
                return {
                    'url': url,
                    'content': content or '',
                    'title': title or '',
                    'meta_description': self._extract_meta_description(html),
                    'method': 'stealth'
                }
                
            finally:
                await browser.close()
    
    async def _scrape_with_proxy(self, url: str) -> Dict:
        """Scrape with proxy"""
        proxy = self._get_next_proxy()
        if not proxy:
            return await self._scrape_with_stealth(url)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                proxy={'server': f'http://{proxy}'}
            )
            
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(3)
                
                html = await page.content()
                title = await page.title()
                content = trafilatura.extract(html)
                
                return {
                    'url': url,
                    'content': content or '',
                    'title': title or '',
                    'meta_description': self._extract_meta_description(html),
                    'method': 'proxy',
                    'proxy': proxy
                }
                
            finally:
                await browser.close()
    
    async def _scrape_with_delays(self, url: str) -> Dict:
        """Scrape with random delays"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="domcontentloaded")
                await asyncio.sleep(5)  # Wait for dynamic content
                
                # Scroll to trigger lazy loading
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
                html = await page.content()
                title = await page.title()
                content = trafilatura.extract(html)
                
                return {
                    'url': url,
                    'content': content or '',
                    'title': title or '',
                    'meta_description': self._extract_meta_description(html),
                    'method': 'delays'
                }
                
            finally:
                await browser.close()
    
    async def _scrape_with_mobile_ua(self, url: str) -> Dict:
        """Scrape with mobile user agent"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                viewport={'width': 375, 'height': 667}
            )
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(3)
                
                html = await page.content()
                title = await page.title()
                content = trafilatura.extract(html)
                
                return {
                    'url': url,
                    'content': content or '',
                    'title': title or '',
                    'meta_description': self._extract_meta_description(html),
                    'method': 'mobile'
                }
                
            finally:
                await browser.close()
    
    async def _scrape_with_rotating_proxies(self, url: str) -> Dict:
        """Scrape with rotating proxies"""
        for proxy in self.proxies[:3]:  # Try first 3 proxies
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        headless=True,
                        proxy={'server': f'http://{proxy}'}
                    )
                    
                    context = await browser.new_context()
                    page = await context.new_page()
                    
                    try:
                        await page.goto(url, wait_until="networkidle", timeout=20000)
                        await asyncio.sleep(2)
                        
                        html = await page.content()
                        title = await page.title()
                        content = trafilatura.extract(html)
                        
                        if content and len(content.strip()) > 100:
                            return {
                                'url': url,
                                'content': content,
                                'title': title or '',
                                'meta_description': self._extract_meta_description(html),
                                'method': 'rotating_proxy',
                                'proxy': proxy
                            }
                            
                    finally:
                        await browser.close()
                        
            except Exception as e:
                logger.warning("proxy_scraping_failed", proxy=proxy, error=str(e))
                continue
        
        return None
    
    async def _detect_spam_protection(self, page: Page) -> bool:
        """Detect common spam protection mechanisms"""
        try:
            # Check for common spam protection indicators
            spam_indicators = [
                'cloudflare',
                'captcha',
                'challenge',
                'blocked',
                'access denied',
                'rate limit',
                'bot detection'
            ]
            
            content = await page.content()
            content_lower = content.lower()
            
            for indicator in spam_indicators:
                if indicator in content_lower:
                    return True
            
            # Check if page is too short (might be blocked)
            text_content = await page.evaluate("document.body.innerText")
            if len(text_content) < 100:
                return True
                
            return False
            
        except Exception:
            return True
    
    def _extract_meta_description(self, html: str) -> str:
        """Extract meta description from HTML"""
        import re
        match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        return match.group(1) if match else ''
    
    def save_to_manual_content(self, result: Dict, output_dir: str = "/app/manual_content") -> str:
        """Save scraping result to manual content file"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename from URL
        parsed_url = urlparse(result['url'])
        filename = parsed_url.netloc.replace('www.', '')
        if parsed_url.path and parsed_url.path != '/':
            path_parts = parsed_url.path.strip('/').replace('/', '_')
            filename += f"_{path_parts}"
        filename += ".json"
        
        # Prepare content data
        content_data = {
            "url": result['url'],
            "title": result['title'],
            "content": result['content'],
            "meta_description": result.get('meta_description', ''),
            "source": "enhanced_scraping",
            "added_at": datetime.now().isoformat(),
            "content_length": len(result['content']),
            "word_count": len(result['content'].split()),
            "scraping_method": result.get('method', 'unknown')
        }
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        logger.info("manual_content_saved", 
                   url=result['url'], 
                   filepath=filepath,
                   content_length=len(result['content']),
                   method=result.get('method', 'unknown'))
        
        return filepath


async def scrape_competitors_enhanced(urls: List[str], output_dir: str = "/app/manual_content") -> Dict:
    """
    Enhanced scraping of competitors with automatic file creation
    """
    scraper = EnhancedScrapingService(proxy_file=None)  # No proxy file for now
    
    results = {
        'successful': [],
        'failed': [],
        'files_created': []
    }
    
    print("=" * 80)
    print("  ENHANCED COMPETITOR SCRAPING")
    print("=" * 80)
    print()
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Scraping {url}")
        
        result = await scraper.scrape_with_enhanced_protection(url)
        
        if result and result.get('content') and len(result['content'].strip()) > 100:
            filepath = scraper.save_to_manual_content(result, output_dir)
            results['successful'].append(result)
            results['files_created'].append(filepath)
            print(f"  ✓ Success: {len(result['content'])} chars, {len(result['content'].split())} words")
            print(f"  ✓ Saved to: {filepath}")
        else:
            results['failed'].append(url)
            print(f"  ✗ Failed: {result.get('error', 'No content extracted')}")
        
        print()
    
    print("=" * 80)
    print("  SCRAPING COMPLETE")
    print("=" * 80)
    print(f"Successful: {len(results['successful'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Files created: {len(results['files_created'])}")
    print()
    
    if results['failed']:
        print("Failed URLs:")
        for url in results['failed']:
            print(f"  - {url}")
        print()
        print("These can be added manually or retried later.")
    
    return results


if __name__ == "__main__":
    # Example usage
    competitor_urls = [
        "https://vaynermedia.com/",
        "https://www.agencyspotter.com/top/marketing-agencies",
        "https://www.dentsu.com/",
        "https://premiermarketingus.com/blog/top-10-marketing-agency-services-every-startup-needs/",
        "https://www.digitalsilk.com/digital-trends/digital-agency-services/",
        "https://ninjapromo.io/best-full-service-digital-marketing-agencies"
    ]
    
    asyncio.run(scrape_competitors_enhanced(competitor_urls))

