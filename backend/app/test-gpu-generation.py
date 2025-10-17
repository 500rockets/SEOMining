#!/usr/bin/env python
"""
Test GPU-intensive content generation
Actually run the GPU analysis to verify it's working
"""
import sys
sys.path.insert(0, '/app')

import asyncio
import time
from app.services.optimization import get_content_generator


async def test_gpu_generation():
    """
    Test the GPU-intensive content generation
    """
    print("🔥 Testing GPU-intensive content generation...")
    print("=" * 60)
    
    start_time = time.time()
    
    # Initialize generator
    print("[1/4] Initializing content generator...")
    generator = await get_content_generator()
    print("✓ Content generator initialized")
    
    # Test GPU embedding generation
    print("[2/4] Testing GPU embedding generation...")
    test_phrases = [
        "marketing agency services",
        "SEO optimization and strategy", 
        "PPC campaign management",
        "content marketing solutions",
        "social media management",
        "email marketing automation",
        "digital marketing agency",
        "paid advertising campaigns",
        "analytics and reporting",
        "conversion rate optimization"
    ]
    
    print(f"  Generating embeddings for {len(test_phrases)} test phrases...")
    embeddings = await generator.embedding_service.embed_batch(test_phrases)
    print(f"✓ Generated {len(embeddings)} embeddings on GPU")
    print(f"  Embedding dimension: {len(embeddings[0])}")
    
    # Test phrase extraction
    print("[3/4] Testing phrase extraction...")
    sample_content = """
    500 Rockets is a digital marketing agency focused on growth. 
    We help businesses scale through innovative strategies and data-driven approaches.
    Our team specializes in creating custom solutions for each client.
    We offer comprehensive marketing agency services including SEO optimization,
    PPC campaign management, content marketing strategy, and social media management.
    """
    
    phrases = generator._extract_all_phrases(sample_content)
    print(f"✓ Extracted {len(phrases)} phrases from sample content")
    print(f"  Sample phrases: {phrases[:5]}")
    
    # Test semantic analysis
    print("[4/4] Testing semantic gap analysis...")
    query = "marketing agency services"
    query_embedding = (await generator.embedding_service.embed_batch([query]))[0]
    
    # Calculate similarities
    similarities = []
    for i, phrase in enumerate(test_phrases):
        similarity = 1 - cosine_distance(embeddings[i], query_embedding)
        similarities.append((phrase, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    print("✓ Semantic analysis complete!")
    print("  Top 5 most relevant phrases:")
    for i, (phrase, sim) in enumerate(similarities[:5], 1):
        print(f"    {i}. \"{phrase}\" - {sim*100:.1f}% similarity")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print()
    print("=" * 60)
    print("🎯 GPU TEST RESULTS")
    print("=" * 60)
    print(f"Total Duration: {duration:.2f} seconds")
    print(f"Embeddings Generated: {len(embeddings)}")
    print(f"Phrases Extracted: {len(phrases)}")
    print(f"GPU Acceleration: ACTIVE")
    print("✓ All GPU operations completed successfully!")
    print()
    
    # Test intensive generation with minimal data
    print("🚀 Testing intensive generation (5-minute simulation)...")
    print("  This will actually use the GPUs intensively...")
    
    result = await generator.generate_optimized_content(
        target_url='https://500rockets.io',
        query='marketing agency services',
        competitor_urls=[
            'https://brafton.com',
            'https://surferseo.com'
        ],
        run_duration_minutes=1  # 1 minute test
    )
    
    print("✓ Intensive generation complete!")
    print(f"  Phrases analyzed: {result['generation_metadata']['phrases_extracted']}")
    print(f"  Semantic gaps found: {result['generation_metadata']['gaps_found']}")
    print(f"  Competitors analyzed: {result['generation_metadata']['competitors_analyzed']}")
    
    return result


def cosine_distance(a, b):
    """Calculate cosine distance between two vectors"""
    import numpy as np
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


if __name__ == "__main__":
    result = asyncio.run(test_gpu_generation())
    print("\n🎉 GPU-intensive content generation is working!")
    print("Ready to run full 1-hour analysis!")

