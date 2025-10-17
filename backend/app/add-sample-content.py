#!/usr/bin/env python
"""
Quick Manual Content Addition
Add competitor content quickly for testing
"""
import sys
sys.path.insert(0, '/app')

from app.services.optimization import get_manual_content_manager


def add_sample_content():
    """Add sample competitor content for testing"""
    manager = get_manual_content_manager()
    
    # Sample content from a top competitor
    sample_content = """
    Thrive Internet Marketing Agency is a full-service digital marketing agency that helps businesses grow their online presence and drive more leads. Our comprehensive marketing services include:
    
    SEO Services and Optimization
    Our SEO services focus on both technical optimization and content strategy to improve your organic visibility. We conduct comprehensive keyword research, optimize your site structure, and create high-quality content that ranks.
    
    PPC Campaign Management
    Our paid advertising services maximize your ROI through strategic campaign management. We specialize in Google Ads, Facebook Ads, and other platforms to drive qualified traffic to your business.
    
    Content Marketing Strategy
    Content marketing is at the heart of modern digital marketing. Our content marketing strategy helps you attract, engage, and convert your target audience through valuable, relevant content.
    
    Social Media Management
    Social media management services help you build and maintain a strong online presence. We create engaging content, manage your social accounts, and drive meaningful interactions with your audience.
    
    Email Marketing Automation
    Email marketing automation allows you to nurture leads and customers at scale. Our email marketing services help you create personalized campaigns that drive engagement and conversions.
    
    What services do marketing agencies offer? Marketing agencies provide comprehensive digital marketing services including SEO optimization, PPC campaign management, content marketing strategy, social media management, email marketing automation, and analytics reporting.
    
    Our marketing agency services help businesses reach their target audience and increase conversions through data-driven strategies and proven methodologies.
    """
    
    # Add the content
    filepath = manager.save_manual_content(
        url="https://thriveagency.com/",
        title="Digital Marketing Agency | Thrive Internet Marketing Agency",
        content=sample_content,
        meta_description="Full-service digital marketing agency offering SEO, PPC, content marketing, social media management, and email marketing services.",
        source="manual_sample"
    )
    
    print("✓ Sample content added successfully!")
    print(f"URL: https://thriveagency.com/")
    print(f"Content Length: {len(sample_content)} characters")
    print(f"Word Count: {len(sample_content.split())} words")
    print(f"Saved to: {filepath}")
    print()
    print("This content will now be used in GPU analysis instead of scraping.")


def list_content():
    """List all manual content"""
    manager = get_manual_content_manager()
    content_list = manager.list_manual_content()
    
    print("Manual Content Library:")
    print("=" * 50)
    
    if not content_list:
        print("No manual content saved yet.")
        return
    
    for i, content in enumerate(content_list, 1):
        print(f"{i}. {content['url']}")
        print(f"   Title: {content['title']}")
        print(f"   Content: {content['content_length']} chars, {content['word_count']} words")
        print(f"   Source: {content['source']}")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_content()
    else:
        add_sample_content()
        print()
        list_content()

