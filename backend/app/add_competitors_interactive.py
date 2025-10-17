#!/usr/bin/env python
"""
Interactive Competitor Content Adder
Easy way to add competitors step by step
"""
import sys
sys.path.insert(0, '/app')

import json
from datetime import datetime
from app.services.optimization import get_manual_content_manager


def add_competitor_interactive():
    """Interactive way to add competitor content"""
    
    print("=" * 80)
    print("  INTERACTIVE COMPETITOR CONTENT ADDER")
    print("=" * 80)
    print()
    
    manager = get_manual_content_manager()
    
    # Missing competitors
    competitors = [
        {
            "url": "https://vaynermedia.com/",
            "name": "VaynerMedia",
            "filename": "vaynermedia.com.json"
        },
        {
            "url": "https://www.agencyspotter.com/top/marketing-agencies",
            "name": "AgencySpotter", 
            "filename": "www.agencyspotter.com_top_marketing-agencies.json"
        },
        {
            "url": "https://www.dentsu.com/",
            "name": "Dentsu",
            "filename": "www.dentsu.com.json"
        },
        {
            "url": "https://premiermarketingus.com/blog/top-10-marketing-agency-services-every-startup-needs/",
            "name": "Premier Marketing",
            "filename": "premiermarketingus.com_blog_top-10-marketing-agency-services-every-startup-needs.json"
        },
        {
            "url": "https://www.digitalsilk.com/digital-trends/digital-agency-services/",
            "name": "Digital Silk",
            "filename": "www.digitalsilk.com_digital-trends_digital-agency-services.json"
        },
        {
            "url": "https://ninjapromo.io/best-full-service-digital-marketing-agencies",
            "name": "Ninja Promo",
            "filename": "ninjapromo.io_best-full-service-digital-marketing-agencies.json"
        }
    ]
    
    print("MISSING COMPETITORS TO ADD:")
    print("-" * 80)
    for i, comp in enumerate(competitors, 1):
        print(f"{i}. {comp['name']}")
        print(f"   URL: {comp['url']}")
        print(f"   File: {comp['filename']}")
        print()
    
    print("INSTRUCTIONS:")
    print("-" * 80)
    print("1. Go to each website in your browser")
    print("2. Copy the main text content (not HTML source)")
    print("3. Paste it when prompted")
    print("4. The tool will create the JSON file automatically")
    print()
    
    # Check if user wants to continue
    response = input("Ready to add competitors? (y/n): ").lower().strip()
    if response != 'y':
        print("Exiting. Run this script again when ready.")
        return
    
    print()
    print("=" * 80)
    print("  ADDING COMPETITORS")
    print("=" * 80)
    
    for i, comp in enumerate(competitors, 1):
        print(f"\n[{i}/{len(competitors)}] Adding {comp['name']}")
        print(f"URL: {comp['url']}")
        print()
        
        # Get title
        title = input("Enter the page title: ").strip()
        if not title:
            title = f"{comp['name']} - Marketing Agency"
        
        # Get meta description
        meta_desc = input("Enter meta description (optional): ").strip()
        if not meta_desc:
            meta_desc = f"Marketing agency services and solutions"
        
        # Get content
        print()
        print("Copy the main content from the website and paste it here.")
        print("Press Ctrl+D (or Ctrl+Z on Windows) when done:")
        print()
        
        content_lines = []
        try:
            while True:
                line = input()
                content_lines.append(line)
        except EOFError:
            pass
        
        content = '\n'.join(content_lines)
        
        if not content.strip():
            print(f"⚠ No content provided for {comp['name']}, skipping...")
            continue
        
        # Save the content
        filepath = manager.save_manual_content(
            url=comp['url'],
            title=title,
            content=content,
            meta_description=meta_desc,
            source="manual"
        )
        
        print(f"✓ Added {comp['name']}")
        print(f"  Content: {len(content)} characters, {len(content.split())} words")
        print(f"  Saved to: {filepath}")
    
    print()
    print("=" * 80)
    print("  ALL COMPETITORS ADDED!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Run: docker-compose exec backend python /app/app/working-gpu-analysis.py")
    print("2. Get ~125 semantic gaps instead of 50")
    print("3. More comprehensive optimization recommendations")


if __name__ == "__main__":
    add_competitor_interactive()

