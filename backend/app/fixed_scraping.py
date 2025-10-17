#!/usr/bin/env python3
"""
Fixed Scraping Script
Uses proper configuration and proxy management
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from urllib.parse import urlparse

# Add the app directory to Python path
sys.path.append('/app')

from app.services.scraping import get_scraping_service
from app.core.config import settings


async def scrape_competitors_with_proxies():
    """Scrape competitors using proper proxy configuration"""
    print("=" * 60)
    print("  SCRAPING WITH PROXY CONFIGURATION")
    print("=" * 60)
    print()
    
    # Initialize scraping service with proxy configuration
    proxy_file = settings.PROXY_FILE if settings.USE_PROXIES else None
    print(f"Proxy configuration:")
    print(f"  USE_PROXIES: {settings.USE_PROXIES}")
    print(f"  PROXY_FILE: {proxy_file}")
    print(f"  DISABLE_DIRECT_CONNECTION: {settings.DISABLE_DIRECT_CONNECTION}")
    print()
    
    scraping_service = get_scraping_service(
        proxy_file=proxy_file,
        headless=True
    )
    
    # Competitor URLs
    urls = [
        "https://vaynermedia.com/",
        "https://www.agencyspotter.com/top/marketing-agencies",
        "https://www.dentsu.com/",
        "https://premiermarketingus.com/blog/top-10-marketing-agency-services-every-startup-needs/",
        "https://www.digitalsilk.com/digital-trends/digital-agency-services/",
        "https://ninjapromo.io/best-full-service-digital-marketing-agencies"
    ]
    
    # Create output directory
    output_dir = "/app/manual_content"
    os.makedirs(output_dir, exist_ok=True)
    
    results = {
        'successful': [],
        'failed': [],
        'files_created': []
    }
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Scraping {url}")
        
        try:
            # Use the scraping service
            result = await scraping_service.scrape_url(
                url=url,
                use_proxy=settings.USE_PROXIES,
                max_retries=3
            )
            
            if result and result.get('content') and len(result['content'].strip()) > 100:
                # Create filename
                parsed_url = urlparse(url)
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
                    "source": "proxy_scraping",
                    "added_at": datetime.now().isoformat(),
                    "content_length": len(result['content']),
                    "word_count": len(result['content'].split()),
                    "scraping_method": "proxy_enabled"
                }
                
                # Save file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                results['successful'].append(result)
                results['files_created'].append(filepath)
                print(f"  ✓ Success: {len(result['content'])} chars, {len(result['content'].split())} words")
                print(f"  ✓ Saved to: {filepath}")
                
            else:
                results['failed'].append(url)
                print(f"  ✗ Failed: No content extracted")
                
        except Exception as e:
            results['failed'].append(url)
            print(f"  ✗ Failed: {str(e)}")
        
        print()
    
    print("=" * 60)
    print("  SCRAPING COMPLETE")
    print("=" * 60)
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
    asyncio.run(scrape_competitors_with_proxies())
