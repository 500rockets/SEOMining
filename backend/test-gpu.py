#!/usr/bin/env python3
"""
Quick GPU test script
Run inside Docker container to verify GPU detection
"""

def test_gpu():
    print("=" * 60)
    print("GPU Detection Test")
    print("=" * 60)
    
    # Test 1: PyTorch CUDA
    print("\n[1] Testing PyTorch CUDA...")
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        print(f"   ✓ PyTorch imported successfully")
        print(f"   CUDA Available: {cuda_available}")
        
        if cuda_available:
            gpu_count = torch.cuda.device_count()
            print(f"   GPU Count: {gpu_count}")
            
            for i in range(gpu_count):
                name = torch.cuda.get_device_name(i)
                memory = torch.cuda.get_device_properties(i).total_memory / 1e9
                print(f"   GPU {i}: {name} ({memory:.2f} GB)")
                
            # Test tensor on GPU
            print("\n   Testing tensor creation on GPU...")
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            z = x @ y
            print(f"   ✓ Successfully created and multiplied tensors on GPU")
            print(f"   Result shape: {z.shape}")
        else:
            print("   ✗ CUDA not available")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Sentence Transformers
    print("\n[2] Testing Sentence Transformers...")
    try:
        from sentence_transformers import SentenceTransformer
        print(f"   ✓ Sentence Transformers imported")
        
        print("   Loading model (this may take a moment)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Small test model
        
        if torch.cuda.is_available():
            model = model.to('cuda')
            print(f"   ✓ Model moved to GPU")
        
        # Test embedding
        print("   Generating test embeddings...")
        texts = ["This is a test sentence.", "GPU acceleration is working!"]
        embeddings = model.encode(texts, convert_to_tensor=True)
        print(f"   ✓ Generated {len(embeddings)} embeddings")
        print(f"   Embedding shape: {embeddings.shape}")
        print(f"   Embeddings on GPU: {embeddings.is_cuda}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Environment variables
    print("\n[3] Checking environment variables...")
    import os
    env_vars = {
        'CUDA_VISIBLE_DEVICES': os.getenv('CUDA_VISIBLE_DEVICES', 'not set'),
        'NVIDIA_VISIBLE_DEVICES': os.getenv('NVIDIA_VISIBLE_DEVICES', 'not set'),
        'USE_LOCAL_GPU': os.getenv('USE_LOCAL_GPU', 'not set'),
        'GPU_BATCH_SIZE': os.getenv('GPU_BATCH_SIZE', 'not set'),
    }
    
    for key, value in env_vars.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("GPU Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_gpu()

