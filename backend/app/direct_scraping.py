#!/usr/bin/env python3
"""
Bypass Config Scraping Script
Direct scraping without config dependencies
"""
import asyncio
import json
import os
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import trafilatura


async def scrape_url_direct(url: str, use_proxy: bool = False) -> dict:
    """Direct scraping without config dependencies"""
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
            print(f"Error: {e}")
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


def save_content(result: dict, output_dir: str = "/app/manual_content") -> str:
    """Save content to JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename
    parsed_url = urlparse(result['url'])
    filename = parsed_url.netloc.replace('www.', '')
    if parsed_url.path and parsed_url.path != '/':
        path_parts = parsed_url.path.strip('/').replace('/', '_')
        filename += f"_{path_parts}"
    filename += ".json"
    
    filepath = os.path.join(output_dir, filename)
    
    # Prepare data
    data = {
        "url": result['url'],
        "title": result['title'],
        "content": result['content'],
        "meta_description": result.get('meta_description', ''),
        "source": "direct_scraping",
        "added_at": datetime.now().isoformat(),
        "content_length": len(result['content']),
        "word_count": len(result['content'].split())
    }
    
    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved: {filepath} ({len(result['content'])} chars)")
    return filepath


async def main():
    """Main scraping function"""
    print("=" * 60)
    print("  DIRECT SCRAPING (NO CONFIG)")
    print("=" * 60)
    print()
    
    urls = [
        "https://vaynermedia.com/",
        "https://www.agencyspotter.com/top/marketing-agencies",
        "https://www.dentsu.com/",
        "https://premiermarketingus.com/blog/top-10-marketing-agency-services-every-startup-needs/",
        "https://www.digitalsilk.com/digital-trends/digital-agency-services/",
        "https://ninjapromo.io/best-full-service-digital-marketing-agencies"
    ]
    
    successful = 0
    failed = 0
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        
        result = await scrape_url_direct(url)
        
        if result['success']:
            save_content(result)
            successful += 1
        else:
            print(f"  ✗ Failed: {result.get('error', 'No content')}")
            failed += 1
        
        print()
    
    print("=" * 60)
    print("  SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print()
    print("Files created in /app/manual_content/")


if __name__ == "__main__":
    asyncio.run(main())
