#!/usr/bin/env python3
"""
Improved Scraping Script
Better timeouts, error handling, and progress tracking
"""
import asyncio
import json
import os
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import trafilatura


async def scrape_url_improved(url: str, timeout: int = 15) -> dict:
    """Improved scraping with better timeouts and error handling"""
    print(f"Scraping {url}...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-dev-shm-usage'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            page.set_default_timeout(timeout * 1000)  # Convert to milliseconds
            
            try:
                # Navigate with timeout
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
                
                # Wait for content to load
                await asyncio.sleep(2)
                
                # Try to wait for main content
                try:
                    await page.wait_for_selector('body', timeout=5000)
                except:
                    pass
                
                html = await page.content()
                title = await page.title()
                content = trafilatura.extract(html)
                
                return {
                    'url': url,
                    'content': content or '',
                    'title': title or '',
                    'meta_description': '',
                    'success': bool(content and len(content.strip()) > 100),
                    'content_length': len(content) if content else 0
                }
                
            except asyncio.TimeoutError:
                print(f"  ⏰ Timeout after {timeout}s")
                return {
                    'url': url,
                    'content': '',
                    'title': '',
                    'meta_description': '',
                    'success': False,
                    'error': f'Timeout after {timeout}s'
                }
            except Exception as e:
                print(f"  ❌ Error: {str(e)[:100]}...")
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
                
    except Exception as e:
        print(f"  💥 Browser error: {str(e)[:100]}...")
        return {
            'url': url,
            'content': '',
            'title': '',
            'meta_description': '',
            'success': False,
            'error': f'Browser error: {str(e)}'
        }


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
        "source": "improved_scraping",
        "added_at": datetime.now().isoformat(),
        "content_length": len(result['content']),
        "word_count": len(result['content'].split())
    }
    
    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Saved: {filepath} ({len(result['content'])} chars)")
    return filepath


async def main():
    """Main scraping function with improved error handling"""
    print("=" * 60)
    print("  IMPROVED SCRAPING WITH TIMEOUTS")
    print("=" * 60)
    print()
    
    # Check what files already exist
    existing_files = []
    if os.path.exists("/app/manual_content"):
        existing_files = os.listdir("/app/manual_content")
    
    print(f"Existing files: {len(existing_files)}")
    for f in existing_files:
        print(f"  - {f}")
    print()
    
    # URLs to scrape
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
    skipped = 0
    
    for i, url in enumerate(urls, 1):
        # Check if file already exists
        parsed_url = urlparse(url)
        filename = parsed_url.netloc.replace('www.', '')
        if parsed_url.path and parsed_url.path != '/':
            path_parts = parsed_url.path.strip('/').replace('/', '_')
            filename += f"_{path_parts}"
        filename += ".json"
        
        if filename in existing_files:
            print(f"[{i}/{len(urls)}] {url}")
            print(f"  ⏭️  Skipped: {filename} already exists")
            skipped += 1
            print()
            continue
        
        print(f"[{i}/{len(urls)}] {url}")
        
        # Try with shorter timeout first
        result = await scrape_url_improved(url, timeout=15)
        
        if result['success']:
            save_content(result)
            successful += 1
        else:
            print(f"  ❌ Failed: {result.get('error', 'No content')}")
            failed += 1
        
        print()
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    print("=" * 60)
    print("  SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print()
    
    if failed > 0:
        print("Failed URLs can be retried or added manually.")
    
    print("Files ready for GPU analysis!")


if __name__ == "__main__":
    asyncio.run(main())
