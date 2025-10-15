#!/usr/bin/env python
"""
Test script for Scraping Service
Validates proxy rotation, content extraction, and Playwright integration
"""
import sys
sys.path.insert(0, '/app')

from app.services.scraping import get_scraping_service, ProxyManager
import structlog

logger = structlog.get_logger(__name__)


def test_proxy_manager():
    """Test proxy manager"""
    print("=" * 60)
    print("Test 1: Proxy Manager")
    print("=" * 60)
    
    # Test loading proxies
    proxy_manager = ProxyManager(proxy_file="/app/config/proxies.txt")
    stats = proxy_manager.get_stats()
    
    print(f"✓ Loaded {stats['total_proxies']} proxies")
    print(f"  Available: {stats['available_proxies']}")
    print(f"  Strategy: {stats['rotation_strategy']}")
    
    # Test rotation
    if stats['total_proxies'] > 0:
        proxy1 = proxy_manager.get_next_proxy()
        proxy2 = proxy_manager.get_next_proxy()
        
        print(f"✓ First proxy: {proxy1.split('@')[1] if '@' in proxy1 else proxy1}")
        print(f"✓ Second proxy: {proxy2.split('@')[1] if '@' in proxy2 else proxy2}")
    
    print()


def test_content_extraction():
    """Test Trafilatura content extraction"""
    print("=" * 60)
    print("Test 2: Content Extraction (Trafilatura)")
    print("=" * 60)
    
    # Sample HTML
    html = """
    <html>
    <head>
        <title>SEO Best Practices 2025</title>
        <meta name="description" content="Learn the latest SEO techniques">
    </head>
    <body>
        <h1>Ultimate Guide to SEO</h1>
        <p>Search engine optimization is crucial for online visibility.</p>
        <h2>On-Page SEO</h2>
        <p>Optimize your title tags, meta descriptions, and content quality.</p>
        <h2>Technical SEO</h2>
        <p>Focus on site speed, mobile responsiveness, and crawlability.</p>
    </body>
    </html>
    """
    
    service = get_scraping_service()
    content = service.extract_content(html, "https://example.com/seo-guide")
    
    if 'error' not in content:
        print(f"✓ Content extracted successfully")
        print(f"  Title: {content.get('title', 'N/A')}")
        print(f"  Text length: {len(content.get('text', ''))}")
        print(f"  Description: {content.get('description', 'N/A')[:60]}...")
    else:
        print(f"✗ Extraction failed: {content['error']}")
    
    print()


def test_scrape_without_proxy():
    """Test scraping without proxy"""
    print("=" * 60)
    print("Test 3: Scrape URL (No Proxy)")
    print("=" * 60)
    
    service = get_scraping_service()
    
    # Test with a simple, reliable URL
    test_url = "https://example.com"
    
    print(f"Scraping: {test_url}")
    result = service.scrape_url(test_url, use_proxy=False, max_retries=2)
    
    if 'error' not in result:
        print(f"✓ Scrape successful")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Text length: {len(result.get('text', ''))}")
        print(f"  Final URL: {result.get('scraping_metadata', {}).get('final_url', 'N/A')}")
    else:
        print(f"✗ Scrape failed: {result['error']}")
    
    print()


def test_scrape_with_proxy():
    """Test scraping with proxy"""
    print("=" * 60)
    print("Test 4: Scrape URL (With Proxy)")
    print("=" * 60)
    
    proxy_manager = ProxyManager(proxy_file="/app/config/proxies.txt")
    service = get_scraping_service(proxy_file="/app/config/proxies.txt")
    
    if proxy_manager.get_stats()['total_proxies'] == 0:
        print("⚠  No proxies available, skipping test")
        print()
        return
    
    # Test with a simple, reliable URL
    test_url = "https://example.com"
    
    print(f"Scraping with proxy rotation: {test_url}")
    result = service.scrape_url(test_url, use_proxy=True, max_retries=2)
    
    if 'error' not in result:
        print(f"✓ Scrape successful")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Proxy used: {result.get('scraping_metadata', {}).get('proxy_used', False)}")
        print(f"  Attempts: {result.get('scraping_metadata', {}).get('attempt', 'N/A')}")
    else:
        print(f"✗ Scrape failed: {result['error']}")
        print(f"  This is expected if proxies are not configured properly")
    
    print()


def test_metadata_extraction():
    """Test metadata-only extraction"""
    print("=" * 60)
    print("Test 5: Metadata Extraction")
    print("=" * 60)
    
    html = """
    <html>
    <head>
        <title>Complete SEO Guide</title>
        <meta name="description" content="Comprehensive SEO tutorial">
        <meta name="author" content="SEO Expert">
        <meta property="og:title" content="SEO Guide">
    </head>
    <body><p>Content here</p></body>
    </html>
    """
    
    service = get_scraping_service()
    metadata = service.extract_metadata_only(html, "https://example.com/guide")
    
    if 'error' not in metadata:
        print(f"✓ Metadata extracted")
        print(f"  Title: {metadata.get('title', 'N/A')}")
        print(f"  Author: {metadata.get('author', 'N/A')}")
        print(f"  Description: {metadata.get('description', 'N/A')}")
    else:
        print(f"✗ Metadata extraction failed: {metadata['error']}")
    
    print()


def test_batch_scraping():
    """Test batch scraping"""
    print("=" * 60)
    print("Test 6: Batch Scraping")
    print("=" * 60)
    
    service = get_scraping_service()
    
    urls = [
        "https://example.com",
        "https://example.org",
    ]
    
    print(f"Scraping {len(urls)} URLs...")
    results = service.scrape_urls_batch(urls, use_proxy=False, delay_between_requests=1.0)
    
    successful = sum(1 for r in results if 'error' not in r)
    failed = sum(1 for r in results if 'error' in r)
    
    print(f"✓ Batch scraping complete")
    print(f"  Successful: {successful}/{len(urls)}")
    print(f"  Failed: {failed}/{len(urls)}")
    
    print()


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print("  SCRAPING SERVICE TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_proxy_manager()
        test_content_extraction()
        test_scrape_without_proxy()
        test_scrape_with_proxy()
        test_metadata_extraction()
        test_batch_scraping()
        
        print("=" * 60)
        print("  ALL TESTS COMPLETED")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

