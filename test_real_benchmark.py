#!/usr/bin/env python3
"""
Test script for real HTTP benchmarking

This script demonstrates the real benchmarking implementation.
It can test against a running llama.cpp server.

Usage:
    # Start llama.cpp server first:
    docker run -d -p 8080:8080 ghcr.io/ggerganov/llama.cpp:server \\
        --model your-model.gguf --host 0.0.0.0 --port 8080
    
    # Then run this test:
    python test_real_benchmark.py
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from real_benchmark import run_real_benchmark
    REAL_BENCHMARKING_AVAILABLE = True
except ImportError as e:
    print(f"❌ Real benchmarking not available: {e}")
    print("Install dependencies: pip install aiohttp")
    REAL_BENCHMARKING_AVAILABLE = False
    sys.exit(1)


async def test_llama_cpp():
    """Test against llama.cpp server"""
    
    print("=" * 70)
    print("Testing Real Benchmarking - llama.cpp")
    print("=" * 70)
    print()
    print("Prerequisites:")
    print("  • llama.cpp server running on http://localhost:8080")
    print("  • Or any OpenAI-compatible API endpoint")
    print()
    
    # Test prompts
    prompts = [
        "What is machine learning?",
        "Explain Python in simple terms.",
        "What are neural networks?",
        "Describe artificial intelligence.",
    ]
    
    # Test configurations
    tests = [
        {"concurrency": 1, "duration": 10, "description": "Single user"},
        {"concurrency": 5, "duration": 10, "description": "5 concurrent users"},
    ]
    
    for test in tests:
        print(f"\n{'─' * 70}")
        print(f"Test: {test['description']}")
        print(f"Concurrency: {test['concurrency']}, Duration: {test['duration']}s")
        print(f"{'─' * 70}")
        
        result = await run_real_benchmark(
            engine='llama.cpp',
            base_url='http://localhost:8080',
            model_name='llama-3.1-8b',
            prompts=prompts,
            concurrency=test['concurrency'],
            duration=test['duration']
        )
        
        if result:
            print(f"\n✅ Benchmark Results:")
            print(f"  TTFT (p50):     {result['ttft_p50']:.3f}s")
            print(f"  TTFT (p95):     {result['ttft_p95']:.3f}s")
            print(f"  TTFT (p99):     {result['ttft_p99']:.3f}s")
            print(f"  Throughput:     {result['tokens_per_sec']:.1f} tok/s")
            print(f"  Total tokens:   {result['total_tokens']}")
            print(f"  Successful:     {result['successful_requests']}")
            print(f"  Failed:         {result['failed_requests']}")
            print(f"  Error rate:     {result['error_rate']*100:.1f}%")
        else:
            print(f"\n❌ Benchmark failed")
            print(f"  Is llama.cpp running on http://localhost:8080?")
            print(f"  Try: curl http://localhost:8080/health")
            break
    
    print(f"\n{'=' * 70}")


async def test_ollama():
    """Test against Ollama server"""
    
    print("\n" + "=" * 70)
    print("Testing Real Benchmarking - Ollama")
    print("=" * 70)
    print()
    print("Prerequisites:")
    print("  • Ollama running on http://localhost:11434")
    print("  • Model pulled: ollama pull llama3.1")
    print()
    
    prompts = ["What is AI?", "Explain Python."]
    
    result = await run_real_benchmark(
        engine='ollama',
        base_url='http://localhost:11434',
        model_name='llama3.1',
        prompts=prompts,
        concurrency=2,
        duration=10
    )
    
    if result:
        print(f"\n✅ Benchmark Results:")
        print(f"  TTFT (p50):     {result['ttft_p50']:.3f}s")
        print(f"  Throughput:     {result['tokens_per_sec']:.1f} tok/s")
        print(f"  Successful:     {result['successful_requests']}")
    else:
        print(f"\n⚠️  Ollama not available - skipping")
    
    print(f"\n{'=' * 70}")


def print_setup_instructions():
    """Print setup instructions"""
    
    print("\n" + "=" * 70)
    print("Setup Instructions")
    print("=" * 70)
    print()
    print("Option 1: Test with llama.cpp")
    print("-" * 70)
    print("# Pull the model (one-time)")
    print("huggingface-cli download bartowski/Meta-Llama-3.1-8B-Instruct-GGUF \\")
    print("  Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf --local-dir ./models")
    print()
    print("# Start server")
    print("docker run -d -p 8080:8080 -v ./models:/models \\")
    print("  ghcr.io/ggerganov/llama.cpp:server \\")
    print("  --model /models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \\")
    print("  --host 0.0.0.0 --port 8080")
    print()
    print("Option 2: Test with Ollama")
    print("-" * 70)
    print("# Install Ollama")
    print("curl -fsSL https://ollama.com/install.sh | sh")
    print()
    print("# Pull model")
    print("ollama pull llama3.1")
    print()
    print("# Ollama runs automatically on http://localhost:11434")
    print()
    print("Option 3: Test with Mock Server (for demo)")
    print("-" * 70)
    print("# Use the included mock server")
    print("python scripts/mock_server.py")
    print()
    print("=" * 70)


async def main():
    """Run all tests"""
    
    print("\n🦙 llamabench - Real Benchmarking Test Suite\n")
    
    # Check if we should run tests or show instructions
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print_setup_instructions()
        return
    
    # Test llama.cpp (most common)
    await test_llama_cpp()
    
    # Optionally test Ollama
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        await test_ollama()
    
    print("\n💡 Tips:")
    print("  • Run with --help to see setup instructions")
    print("  • Run with --all to test all engines")
    print("  • Make sure engines are running before testing")
    print()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
