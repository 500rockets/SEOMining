"""
Simple Scraping Service
Creates manual content files automatically
"""
import asyncio
import json
import os
from typing import Dict, List
from datetime import datetime
from playwright.async_api import async_playwright
import trafilatura
from urllib.parse import urlparse


async def scrape_url_simple(url: str) -> Dict:
    """Simple scraping with basic protection"""
    print(f"Scraping {url}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
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
                'meta_description': '',
                'success': bool(content and len(content.strip()) > 100)
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'content': '',
                'title': '',
                'meta_description': '',
                'success': False,
                'error': str(e)
            }
        finally:
            await browser.close()


def save_to_manual_content(result: Dict, output_dir: str = "/app/manual_content") -> str:
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
        "source": "simple_scraping",
        "added_at": datetime.now().isoformat(),
        "content_length": len(result['content']),
        "word_count": len(result['content'].split())
    }
    
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved to: {filepath}")
    return filepath


async def scrape_competitors_simple(urls: List[str]) -> Dict:
    """Simple scraping of competitors"""
    print("=" * 60)
    print("  SIMPLE COMPETITOR SCRAPING")
    print("=" * 60)
    print()
    
    results = {
        'successful': [],
        'failed': [],
        'files_created': []
    }
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        
        result = await scrape_url_simple(url)
        
        if result['success']:
            filepath = save_to_manual_content(result)
            results['successful'].append(result)
            results['files_created'].append(filepath)
            print(f"  ✓ Success: {len(result['content'])} chars, {len(result['content'].split())} words")
        else:
            results['failed'].append(url)
            print(f"  ✗ Failed: {result.get('error', 'No content')}")
        
        print()
    
    print("=" * 60)
    print("  SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Successful: {len(results['successful'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Files created: {len(results['files_created'])}")
    
    return results


if __name__ == "__main__":
    competitor_urls = [
        "https://vaynermedia.com/",
        "https://www.agencyspotter.com/top/marketing-agencies",
        "https://www.dentsu.com/",
        "https://premiermarketingus.com/blog/top-10-marketing-agency-services-every-startup-needs/",
        "https://www.digitalsilk.com/digital-trends/digital-agency-services/",
        "https://ninjapromo.io/best-full-service-digital-marketing-agencies"
    ]
    
    asyncio.run(scrape_competitors_simple(competitor_urls))
