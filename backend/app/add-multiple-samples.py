#!/usr/bin/env python
"""
Add Multiple Competitor Samples
Add several competitor content samples for comprehensive analysis
"""
import sys
sys.path.insert(0, '/app')

from app.services.optimization import get_manual_content_manager


def add_multiple_samples():
    """Add multiple competitor content samples"""
    manager = get_manual_content_manager()
    
    competitors = [
        {
            "url": "https://brasco.marketing/what-services-do-marketing-agencies-offer/",
            "title": "What Services Do Marketing Agencies Offer? - Brasco",
            "content": """
            What services do marketing agencies offer? Marketing agencies provide comprehensive digital marketing services to help businesses grow their online presence and drive more leads.
            
            Marketing agency services typically include:
            
            SEO Services and Optimization
            Search engine optimization helps improve your website's visibility in search results. Our SEO services include keyword research, on-page optimization, technical SEO, and content strategy.
            
            PPC Campaign Management
            Pay-per-click advertising allows you to reach your target audience through paid search and display ads. We manage Google Ads, Facebook Ads, and other PPC platforms to maximize your ROI.
            
            Content Marketing Strategy
            Content marketing focuses on creating valuable, relevant content that attracts and engages your target audience. This includes blog posts, videos, infographics, and other content formats.
            
            Social Media Management
            Social media management helps you build and maintain a strong presence on social platforms. We create engaging content, manage your accounts, and drive meaningful interactions.
            
            Email Marketing Automation
            Email marketing automation allows you to nurture leads and customers at scale. We create personalized campaigns that drive engagement and conversions.
            
            Analytics and Reporting
            Data-driven insights help optimize your marketing performance. We provide detailed reporting and analytics to track progress and identify opportunities.
            
            These marketing agency services work together to create a comprehensive digital marketing strategy that drives results for your business.
            """,
            "meta_description": "Learn what services marketing agencies offer including SEO, PPC, content marketing, social media management, and email marketing automation."
        },
        {
            "url": "https://surferseo.com/blog/marketing-agency/",
            "title": "Everything Marketing Agencies Do in 2025",
            "content": """
            Everything marketing agencies do in 2025 encompasses comprehensive digital marketing services designed to help businesses grow and scale effectively.
            
            Marketing agency services include:
            
            Full-Service Digital Marketing
            Marketing agencies provide end-to-end digital marketing solutions including strategy development, implementation, and optimization across all channels.
            
            SEO and Content Marketing
            Search engine optimization and content marketing work together to improve organic visibility and attract qualified traffic to your website.
            
            Paid Advertising Management
            PPC campaign management includes Google Ads, Facebook Ads, and other paid advertising platforms to drive targeted traffic and conversions.
            
            Social Media Marketing
            Social media management and advertising help you build brand awareness, engage with your audience, and drive traffic to your website.
            
            Email Marketing Services
            Email marketing automation and campaign management help nurture leads and maintain customer relationships through personalized communications.
            
            Conversion Rate Optimization
            CRO services focus on improving your website's ability to convert visitors into customers through testing and optimization.
            
            Marketing agencies offer these services as part of comprehensive marketing strategies that drive measurable results for businesses of all sizes.
            """,
            "meta_description": "Discover everything marketing agencies do in 2025 including SEO, PPC, content marketing, social media, and email marketing services."
        },
        {
            "url": "https://www.brafton.com/blog/content-marketing/what-do-marketing-agencies-do/",
            "title": "What Do Marketing Agencies Do, Anyway? (Infographic) | Brafton",
            "content": """
            What do marketing agencies do? Marketing agencies provide comprehensive digital marketing services to help businesses reach their target audience and achieve their marketing goals.
            
            Marketing agency services typically include:
            
            Digital Marketing Strategy
            Marketing agencies develop comprehensive digital marketing strategies tailored to your business goals, target audience, and competitive landscape.
            
            Content Marketing Services
            Content marketing includes blog writing, video production, infographic design, and other content creation services that engage your audience.
            
            SEO and Search Marketing
            Search engine optimization and search marketing help improve your website's visibility and drive organic traffic through strategic optimization.
            
            Social Media Marketing
            Social media management and advertising services help you build brand awareness and engage with your audience across all platforms.
            
            Email Marketing Campaigns
            Email marketing services include campaign development, automation setup, and performance optimization to nurture leads and customers.
            
            Paid Advertising Management
            PPC and paid advertising services manage your Google Ads, Facebook Ads, and other paid campaigns to drive targeted traffic.
            
            Analytics and Performance Tracking
            Marketing agencies provide detailed analytics and reporting to track performance and optimize campaigns for better results.
            
            These marketing agency services work together to create integrated marketing campaigns that drive growth and success for your business.
            """,
            "meta_description": "Learn what marketing agencies do including digital marketing strategy, content marketing, SEO, social media, and paid advertising services."
        }
    ]
    
    print("Adding multiple competitor content samples...")
    print()
    
    for i, comp in enumerate(competitors, 1):
        print(f"[{i}/{len(competitors)}] Adding {comp['url']}")
        
        filepath = manager.save_manual_content(
            url=comp['url'],
            title=comp['title'],
            content=comp['content'],
            meta_description=comp['meta_description'],
            source="manual_sample"
        )
        
        print(f"✓ Added {len(comp['content'])} characters, {len(comp['content'].split())} words")
    
    print()
    print("✓ All competitor samples added successfully!")
    print()
    
    # List all content
    content_list = manager.list_manual_content()
    print(f"Total manual content: {len(content_list)} competitors")
    for content in content_list:
        print(f"  - {content['url']} ({content['word_count']} words)")


if __name__ == "__main__":
    add_multiple_samples()

