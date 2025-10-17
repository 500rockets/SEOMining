#!/usr/bin/env python
"""
Manual Competitor Content Adder
Easy way to add remaining competitors for full analysis
"""
import sys
sys.path.insert(0, '/app')

import json
import os
from datetime import datetime
from app.services.optimization import get_manual_content_manager


def show_remaining_competitors():
    """Show which competitors we still need to add"""
    
    print("=" * 80)
    print("  REMAINING COMPETITORS TO ADD")
    print("=" * 80)
    print()
    
    # List of all competitors from the analysis
    all_competitors = [
        {
            "url": "https://thriveagency.com/",
            "name": "Thrive Agency",
            "status": "✓ Added"
        },
        {
            "url": "https://brasco.marketing/what-services-do-marketing-agencies-offer/",
            "name": "Brasco Marketing",
            "status": "✓ Added"
        },
        {
            "url": "https://surferseo.com/blog/marketing-agency/",
            "name": "SurferSEO",
            "status": "✓ Added"
        },
        {
            "url": "https://www.brafton.com/blog/content-marketing/what-do-marketing-agencies-do/",
            "name": "Brafton",
            "status": "✓ Added"
        },
        {
            "url": "https://vaynermedia.com/",
            "name": "VaynerMedia",
            "status": "❌ Missing"
        },
        {
            "url": "https://www.agencyspotter.com/top/marketing-agencies",
            "name": "AgencySpotter",
            "status": "❌ Missing"
        },
        {
            "url": "https://www.dentsu.com/",
            "name": "Dentsu",
            "status": "❌ Missing"
        },
        {
            "url": "https://premiermarketingus.com/blog/top-10-marketing-agency-services-every-startup-needs/",
            "name": "Premier Marketing",
            "status": "❌ Missing"
        },
        {
            "url": "https://www.digitalsilk.com/digital-trends/digital-agency-services/",
            "name": "Digital Silk",
            "status": "❌ Missing"
        },
        {
            "url": "https://ninjapromo.io/best-full-service-digital-marketing-agencies",
            "name": "Ninja Promo",
            "status": "❌ Missing"
        }
    ]
    
    print("COMPETITOR STATUS:")
    print("-" * 80)
    for i, comp in enumerate(all_competitors, 1):
        print(f"{i:2}. {comp['status']} {comp['name']}")
        print(f"    {comp['url']}")
        print()
    
    print("MISSING COMPETITORS (6):")
    print("-" * 80)
    missing = [comp for comp in all_competitors if "Missing" in comp['status']]
    for comp in missing:
        print(f"• {comp['name']} - {comp['url']}")
    print()
    
    print("HOW TO ADD MISSING COMPETITORS:")
    print("-" * 80)
    print("1. Go to each website manually")
    print("2. Copy the main content (not HTML source)")
    print("3. Use the add_competitor() function below")
    print("4. Or create JSON files manually")
    print()
    
    print("FILE NAMING CONVENTION:")
    print("-" * 80)
    print("URL: https://vaynermedia.com/")
    print("File: vaynermedia.com.json")
    print()
    print("URL: https://www.agencyspotter.com/top/marketing-agencies")
    print("File: www.agencyspotter.com_top_marketing-agencies.json")
    print()
    print("URL: https://premiermarketingus.com/blog/top-10-marketing-agency-services-every-startup-needs/")
    print("File: premiermarketingus.com_blog_top-10-marketing-agency-services-every-startup-needs.json")
    print()


def add_competitor(url, title, content, meta_description=""):
    """Add a competitor manually"""
    manager = get_manual_content_manager()
    
    filepath = manager.save_manual_content(
        url=url,
        title=title,
        content=content,
        meta_description=meta_description,
        source="manual"
    )
    
    print(f"✓ Added competitor: {url}")
    print(f"  Title: {title}")
    print(f"  Content: {len(content)} characters, {len(content.split())} words")
    print(f"  Saved to: {filepath}")
    print()


def show_file_format():
    """Show the exact JSON format for manual files"""
    
    print("EXACT JSON FORMAT:")
    print("-" * 80)
    print("""
{
  "url": "https://vaynermedia.com/",
  "title": "VaynerMedia : Integrated Strategy, Creative and Media Agency",
  "content": "PASTE THE MAIN CONTENT HERE (not HTML source, just the text content)",
  "meta_description": "Integrated marketing solutions and agency services",
  "source": "manual",
  "added_at": "2025-10-16T00:00:00.000000",
  "content_length": 1234,
  "word_count": 200
}
""")
    print()
    print("INSTRUCTIONS:")
    print("-" * 80)
    print("1. Go to the competitor website")
    print("2. Copy the main text content (not HTML source)")
    print("3. Create a JSON file with the format above")
    print("4. Save it in /app/manual_content/ with the right filename")
    print("5. Run the GPU analysis again")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "format":
            show_file_format()
        elif command == "list":
            show_remaining_competitors()
        else:
            print("Usage: python add_competitors.py [list|format]")
    else:
        show_remaining_competitors()
        print()
        show_file_format()

