#!/usr/bin/env python
"""
Add Target Content Sample
Add 500rockets.io content manually for analysis
"""
import sys
sys.path.insert(0, '/app')

from app.services.optimization import get_manual_content_manager


def add_target_content():
    """Add 500rockets.io content sample"""
    manager = get_manual_content_manager()
    
    target_content = """
    500 Rockets is a digital marketing agency focused on growth and innovation. 
    We help businesses scale through data-driven strategies and cutting-edge marketing solutions.
    
    Our team specializes in creating custom marketing strategies for each client, 
    focusing on measurable results and sustainable growth. We combine creativity with 
    analytics to deliver marketing campaigns that work.
    
    At 500 Rockets, we believe in the power of strategic marketing to transform businesses. 
    Our approach combines traditional marketing principles with modern digital tools 
    to create comprehensive solutions that drive real results.
    
    We work with businesses of all sizes, from startups to established companies, 
    helping them navigate the complex world of digital marketing and achieve their goals.
    
    Our services include strategic planning, campaign development, performance analysis, 
    and ongoing optimization to ensure maximum ROI for our clients.
    """
    
    filepath = manager.save_manual_content(
        url="https://500rockets.io",
        title="Launch 500 Rockets - Rebuild the Three That Work | 500 Rockets Marketing",
        content=target_content,
        meta_description="500 Rockets is a digital marketing agency focused on growth and innovation. We help businesses scale through data-driven strategies.",
        source="manual_target"
    )
    
    print("✓ Target content added successfully!")
    print(f"URL: https://500rockets.io")
    print(f"Content Length: {len(target_content)} characters")
    print(f"Word Count: {len(target_content.split())} words")
    print(f"Saved to: {filepath}")
    print()
    print("Now we can run GPU analysis with both target and competitor content!")


if __name__ == "__main__":
    add_target_content()

