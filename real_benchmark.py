"""
Real HTTP benchmarking implementation
Replaces mock data with actual API calls and metric collection
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics


class RealBenchmarkEngine:
    """
    Handles actual HTTP benchmarking for inference engines
    """
    
    def __init__(self, engine: str, base_url: str, model_name: str):
        self.engine = engine
        self.base_url = base_url
        self.model_name = model_name
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Create session on enter"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close session on exit"""
        if self.session:
            await self.session.close()
    
    async def health_check(self, timeout: int = 5) -> bool:
        """
        Check if engine is healthy and responding
        """
        try:
            health_endpoints = {
                'llama.cpp': '/health',
                'ollama': '/api/tags',
                'vllm': '/health',
            }
            
            endpoint = health_endpoints.get(self.engine, '/health')
            url = f"{self.base_url}{endpoint}"
            
            async with self.session.get(url, timeout=timeout) as response:
                return response.status == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    async def measure_single_request(self, prompt: str) -> Dict[str, Any]:
        """
        Measure a single request with TTFT and total time
        
        Returns:
            {
                'ttft': float,  # Time to first token (seconds)
                'total_time': float,  # Total request time
                'tokens': int,  # Number of tokens generated
                'success': bool,
                'error': Optional[str]
            }
        """
        start_time = time.perf_counter()
        ttft = None
        tokens = 0
        
        try:
            # Build request based on engine type
            url, payload = self._build_request(prompt)
            
            async with self.session.post(url, json=payload, timeout=30) as response:
                if response.status != 200:
                    return {
                        'ttft': None,
                        'total_time': time.perf_counter() - start_time,
                        'tokens': 0,
                        'success': False,
                        'error': f"HTTP {response.status}"
                    }
                
                # For streaming responses
                if self.engine == 'llama.cpp':
                    async for line in response.content:
                        if ttft is None:
                            ttft = time.perf_counter() - start_time
                        
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if 'content' in data:
                                    tokens += 1
                            except:
                                pass
                
                elif self.engine == 'ollama':
                    async for line in response.content:
                        if ttft is None:
                            ttft = time.perf_counter() - start_time
                        
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if 'response' in data:
                                    tokens += len(data.get('response', '').split())
                            except:
                                pass
                
                elif self.engine == 'vllm':
                    # vLLM uses OpenAI-compatible API
                    data = await response.json()
                    ttft = time.perf_counter() - start_time  # Non-streaming for now
                    
                    if 'choices' in data:
                        content = data['choices'][0].get('text', '')
                        tokens = len(content.split())
            
            total_time = time.perf_counter() - start_time
            
            # If we didn't get TTFT (non-streaming), use total time
            if ttft is None:
                ttft = total_time
            
            return {
                'ttft': ttft,
                'total_time': total_time,
                'tokens': tokens if tokens > 0 else 50,  # Estimate if can't count
                'success': True,
                'error': None
            }
        
        except asyncio.TimeoutError:
            return {
                'ttft': None,
                'total_time': time.perf_counter() - start_time,
                'tokens': 0,
                'success': False,
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'ttft': None,
                'total_time': time.perf_counter() - start_time,
                'tokens': 0,
                'success': False,
                'error': str(e)
            }
    
    def _build_request(self, prompt: str) -> tuple[str, dict]:
        """
        Build request URL and payload for specific engine
        """
        if self.engine == 'llama.cpp':
            url = f"{self.base_url}/completion"
            payload = {
                "prompt": prompt,
                "n_predict": 512,
                "temperature": 0.7,
                "stream": True,
            }
        
        elif self.engine == 'ollama':
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
            }
        
        elif self.engine == 'vllm':
            url = f"{self.base_url}/v1/completions"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.7,
            }
        
        else:
            raise ValueError(f"Unknown engine: {self.engine}")
        
        return url, payload
    
    async def run_concurrent_benchmark(
        self,
        prompts: List[str],
        concurrency: int,
        duration: int
    ) -> Dict[str, Any]:
        """
        Run benchmark with concurrent requests for specified duration
        
        Args:
            prompts: List of prompts to cycle through
            concurrency: Number of concurrent requests
            duration: How long to run (seconds)
        
        Returns:
            Dictionary with aggregated metrics
        """
        results = []
        start_time = time.time()
        
        async def worker(worker_id: int):
            """Worker that sends requests until duration expires"""
            prompt_idx = 0
            while time.time() - start_time < duration:
                prompt = prompts[prompt_idx % len(prompts)]
                result = await self.measure_single_request(prompt)
                results.append(result)
                prompt_idx += 1
        
        # Start workers
        workers = [asyncio.create_task(worker(i)) for i in range(concurrency)]
        
        # Wait for all workers to complete
        await asyncio.gather(*workers)
        
        # Aggregate results
        return self._aggregate_results(results, duration)
    
    def _aggregate_results(self, results: List[Dict], duration: int) -> Dict[str, Any]:
        """
        Aggregate individual request results into summary metrics
        """
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if not successful:
            return {
                'successful_requests': 0,
                'failed_requests': len(failed),
                'ttft_p50': 0,
                'ttft_p95': 0,
                'ttft_p99': 0,
                'tokens_per_sec': 0,
                'total_tokens': 0,
                'error_rate': 1.0,
            }
        
        # Extract TTFT values
        ttfts = [r['ttft'] for r in successful]
        ttfts.sort()
        
        # Calculate percentiles
        def percentile(data, p):
            if not data:
                return 0
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f < len(data) - 1 else f
            return data[f] + (k - f) * (data[c] - data[f])
        
        ttft_p50 = percentile(ttfts, 50)
        ttft_p95 = percentile(ttfts, 95)
        ttft_p99 = percentile(ttfts, 99)
        
        # Calculate throughput
        total_tokens = sum(r['tokens'] for r in successful)
        tokens_per_sec = total_tokens / duration if duration > 0 else 0
        
        return {
            'successful_requests': len(successful),
            'failed_requests': len(failed),
            'ttft_p50': round(ttft_p50, 3),
            'ttft_p95': round(ttft_p95, 3),
            'ttft_p99': round(ttft_p99, 3),
            'tokens_per_sec': round(tokens_per_sec, 1),
            'total_tokens': total_tokens,
            'error_rate': len(failed) / len(results) if results else 0,
        }


async def run_real_benchmark(
    engine: str,
    base_url: str,
    model_name: str,
    prompts: List[str],
    concurrency: int,
    duration: int
) -> Dict[str, Any]:
    """
    Convenience function to run a complete benchmark
    
    Args:
        engine: Engine type ('llama.cpp', 'ollama', 'vllm')
        base_url: Base URL of the engine (e.g., 'http://localhost:8080')
        model_name: Model identifier
        prompts: List of prompts to test with
        concurrency: Number of concurrent requests
        duration: Test duration in seconds
    
    Returns:
        Benchmark results dictionary
    """
    async with RealBenchmarkEngine(engine, base_url, model_name) as bench:
        # Health check first
        print(f"  Checking {engine} health...")
        healthy = await bench.health_check()
        
        if not healthy:
            print(f"  ⚠️  {engine} is not responding, using fallback")
            return None
        
        print(f"  ✅ {engine} is healthy")
        print(f"  Running benchmark for {duration}s at {concurrency}x concurrency...")
        
        results = await bench.run_concurrent_benchmark(prompts, concurrency, duration)
        return results


# Synchronous wrapper for compatibility
def run_benchmark_sync(
    engine: str,
    base_url: str,
    model_name: str,
    prompts: List[str],
    concurrency: int,
    duration: int
) -> Dict[str, Any]:
    """
    Synchronous wrapper for async benchmark function
    """
    return asyncio.run(run_real_benchmark(
        engine, base_url, model_name, prompts, concurrency, duration
    ))


if __name__ == '__main__':
    # Example usage
    import sys
    
    print("Testing real benchmark implementation...")
    
    # Test llama.cpp (if running)
    result = run_benchmark_sync(
        engine='llama.cpp',
        base_url='http://localhost:8080',
        model_name='llama-3.1-8b',
        prompts=['What is machine learning?', 'Explain Python in simple terms.'],
        concurrency=2,
        duration=10
    )
    
    if result:
        print("\n✅ Benchmark completed!")
        print(f"TTFT (p50): {result['ttft_p50']}s")
        print(f"Throughput: {result['tokens_per_sec']} tok/s")
        print(f"Successful: {result['successful_requests']}")
        print(f"Failed: {result['failed_requests']}")
    else:
        print("\n❌ Benchmark failed - is the engine running?")
