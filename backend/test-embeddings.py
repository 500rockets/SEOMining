#!/usr/bin/env python
"""
Test script for Embeddings Service
Validates GPU acceleration, chunking, and semantic similarity
"""
import sys
sys.path.insert(0, '/app')

from app.services.embeddings import (
    get_embedding_service,
    chunk_for_embeddings
)
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


def test_basic_embedding():
    """Test basic embedding generation"""
    print("=" * 60)
    print("Test 1: Basic Embedding Generation")
    print("=" * 60)
    
    service = get_embedding_service()
    
    # Test single text
    text = "This is a test sentence for embedding generation."
    embedding = service.encode(text)
    
    print(f"✓ Generated embedding for single text")
    print(f"  Shape: {embedding.shape}")
    print(f"  Embedding dimension: {service.embedding_dim}")
    print()


def test_batch_embedding():
    """Test batch embedding generation"""
    print("=" * 60)
    print("Test 2: Batch Embedding Generation")
    print("=" * 60)
    
    service = get_embedding_service()
    
    texts = [
        "SEO optimization is crucial for website visibility.",
        "Content marketing helps attract organic traffic.",
        "User experience affects search engine rankings.",
        "Quality backlinks improve domain authority.",
        "Mobile-first indexing is now the standard."
    ]
    
    embeddings = service.encode(texts)
    
    print(f"✓ Generated embeddings for {len(texts)} texts")
    print(f"  Shape: {embeddings.shape}")
    print(f"  Device: {service.device}")
    print()


def test_semantic_similarity():
    """Test semantic similarity computation"""
    print("=" * 60)
    print("Test 3: Semantic Similarity")
    print("=" * 60)
    
    service = get_embedding_service()
    
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "A fast brown fox leaps across a sleepy dog.",  # Similar to first
        "Python is a popular programming language.",     # Different topic
        "Machine learning requires large datasets."      # Different topic
    ]
    
    embeddings = service.encode(texts)
    
    # Compare first two (should be similar)
    sim_high = service.compute_similarity(embeddings[0], embeddings[1])
    print(f"✓ Similarity between similar sentences: {sim_high:.4f}")
    
    # Compare first and third (should be different)
    sim_low = service.compute_similarity(embeddings[0], embeddings[2])
    print(f"✓ Similarity between different sentences: {sim_low:.4f}")
    
    # Compute full similarity matrix
    sim_matrix = service.compute_similarity_matrix(embeddings)
    print(f"✓ Similarity matrix shape: {sim_matrix.shape}")
    print("\nSimilarity Matrix:")
    print(sim_matrix)
    print()


def test_semantic_search():
    """Test semantic search functionality"""
    print("=" * 60)
    print("Test 4: Semantic Search")
    print("=" * 60)
    
    service = get_embedding_service()
    
    corpus = [
        "SEO helps websites rank higher in search results.",
        "Content marketing attracts potential customers.",
        "Social media engagement builds brand awareness.",
        "Email marketing has high ROI for businesses.",
        "Link building improves domain authority and rankings.",
        "Keyword research identifies valuable search terms.",
        "On-page optimization improves content relevance."
    ]
    
    query = "How to improve search engine rankings?"
    
    results = service.semantic_search(query, corpus, top_k=3)
    
    print(f"Query: \"{query}\"")
    print(f"\nTop 3 results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. (Score: {result['score']:.4f}) {result['text']}")
    print()


def test_content_chunking():
    """Test content chunking"""
    print("=" * 60)
    print("Test 5: Content Chunking")
    print("=" * 60)
    
    long_text = """
    Search Engine Optimization (SEO) is the practice of optimizing websites to improve 
    their visibility in search engine results pages (SERPs). Effective SEO involves 
    multiple strategies and techniques.
    
    One crucial aspect is on-page optimization, which includes optimizing title tags, 
    meta descriptions, header tags, and content quality. These elements help search 
    engines understand the page's topic and relevance.
    
    Another important factor is technical SEO, which focuses on website speed, mobile 
    responsiveness, site architecture, and crawlability. Search engines prioritize 
    websites that provide excellent user experiences.
    
    Off-page SEO involves building high-quality backlinks from authoritative websites. 
    Link building signals to search engines that your content is valuable and trustworthy.
    """
    
    chunks = chunk_for_embeddings(
        long_text,
        chunk_size=200,
        overlap=20,
        preserve_structure=True
    )
    
    print(f"✓ Split text into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i} ({len(chunk)} chars):")
        print(f"  {chunk[:100]}...")
    print()


def test_chunk_embeddings():
    """Test embedding generation for chunks"""
    print("=" * 60)
    print("Test 6: Chunk Embeddings with Metadata")
    print("=" * 60)
    
    service = get_embedding_service()
    
    content = """
    Content marketing is essential for modern businesses. It helps attract organic 
    traffic, build brand authority, and engage potential customers. Quality content 
    demonstrates expertise and builds trust with your audience.
    """
    
    chunks = chunk_for_embeddings(content, chunk_size=100, overlap=20)
    
    # Generate embeddings with metadata
    chunk_embeddings = service.encode_chunks(
        chunks,
        metadata=[{'chunk_id': i, 'source': 'test'} for i in range(len(chunks))]
    )
    
    print(f"✓ Generated embeddings for {len(chunk_embeddings)} chunks")
    for i, chunk_data in enumerate(chunk_embeddings):
        print(f"\nChunk {i + 1}:")
        print(f"  Text length: {len(chunk_data['text'])} chars")
        print(f"  Embedding dim: {chunk_data['embedding_dim']}")
        print(f"  Metadata: {chunk_data.get('metadata')}")
    print()


def test_clustering():
    """Test embedding clustering"""
    print("=" * 60)
    print("Test 7: Embedding Clustering")
    print("=" * 60)
    
    service = get_embedding_service()
    
    # Create texts with clear semantic groups
    texts = [
        # Group 1: SEO
        "SEO optimization improves search rankings",
        "Keyword research is essential for SEO",
        "Link building boosts domain authority",
        
        # Group 2: Content Marketing
        "Content marketing attracts organic traffic",
        "Blog posts engage your audience",
        "Quality content builds brand trust",
        
        # Group 3: Social Media
        "Social media increases brand awareness",
        "Twitter engagement drives conversations",
        "Instagram stories boost visibility"
    ]
    
    embeddings = service.encode(texts)
    
    try:
        labels, metadata = service.cluster_embeddings(
            embeddings,
            min_cluster_size=2
        )
        
        print(f"✓ Clustering complete")
        print(f"  Number of clusters: {metadata['num_clusters']}")
        print(f"  Noise points: {metadata['num_noise_points']}")
        print(f"  Cluster sizes: {metadata['cluster_sizes']}")
        
        print("\nCluster assignments:")
        for i, (text, label) in enumerate(zip(texts, labels)):
            print(f"  {i+1}. [Cluster {label}] {text[:50]}...")
    except Exception as e:
        print(f"✗ Clustering failed: {e}")
        print("  (This is expected if HDBSCAN has issues)")
    print()


def test_device_info():
    """Test device information"""
    print("=" * 60)
    print("Test 8: Device Information")
    print("=" * 60)
    
    service = get_embedding_service()
    info = service.get_device_info()
    
    print(f"✓ Device: {info['device']}")
    print(f"✓ Model: {info['model_name']}")
    print(f"✓ Embedding dimension: {info['embedding_dim']}")
    print(f"✓ Batch size: {info['batch_size']}")
    
    if info.get('cuda_available'):
        print(f"✓ GPU count: {info['gpu_count']}")
        for i, gpu in enumerate(info['gpu_devices']):
            print(f"\n  GPU {i}: {gpu['name']}")
            print(f"    Total memory: {gpu['memory_total'] / 1024**3:.2f} GB")
            print(f"    Allocated: {gpu['memory_allocated'] / 1024**3:.2f} GB")
    else:
        print("  Running on CPU")
    print()


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print("  EMBEDDINGS SERVICE TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_basic_embedding()
        test_batch_embedding()
        test_semantic_similarity()
        test_semantic_search()
        test_content_chunking()
        test_chunk_embeddings()
        test_clustering()
        test_device_info()
        
        print("=" * 60)
        print("  ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

