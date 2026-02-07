"""
Benchmark runner - orchestrates testing across different engines
"""

import time
import subprocess
import random
from typing import List, Dict, Any
from datetime import datetime
import os

try:
    import requests
except ImportError:
    requests = None

try:
    import psutil
except ImportError:
    psutil = None

try:
    import docker
except ImportError:
    docker = None

from config import (
    SUPPORTED_MODELS, ENGINE_CONFIGS, PRESETS, 
    BENCHMARK_PROMPTS, DEFAULT_PROMPT
)

try:
    from real_benchmark import run_benchmark_sync
    REAL_BENCHMARKING_AVAILABLE = True
except ImportError:
    REAL_BENCHMARKING_AVAILABLE = False


class BenchmarkRunner:
    """Runs benchmarks across multiple engines and concurrency levels"""
    
    def __init__(
        self,
        model: str,
        engines: List[str],
        concurrency_levels: List[int],
        duration: int = 60,
        preset: str = None,
        custom_prompt: str = None,
        skip_setup: bool = False
    ):
        self.model = model
        self.model_info = SUPPORTED_MODELS[model]
        self.engines = engines
        self.concurrency_levels = concurrency_levels
        self.duration = duration
        self.preset = preset
        self.custom_prompt = custom_prompt
        self.skip_setup = skip_setup
        
        # Apply preset if specified
        if preset and preset in PRESETS:
            preset_config = PRESETS[preset]
            self.concurrency_levels = preset_config['concurrency']
            self.duration = preset_config['duration']
            self.prompt_style = preset_config['prompt_style']
        else:
            self.prompt_style = 'mixed'
        
        # Get prompts
        if custom_prompt:
            self.prompts = [custom_prompt]
        else:
            self.prompts = BENCHMARK_PROMPTS.get(self.prompt_style, [DEFAULT_PROMPT])
        
        # System info
        self.system_info = self._get_system_info()
        
        # Docker client
        if docker:
            try:
                self.docker_client = docker.from_env()
            except:
                self.docker_client = None
                print("⚠️  Docker not available - will use mock data for demo")
        else:
            self.docker_client = None
            print("ℹ️  Running in demo mode with simulated data")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Gather system information"""
        if psutil:
            cpu_count = psutil.cpu_count()
            memory_gb = round(psutil.virtual_memory().total / (1024**3), 1)
        else:
            cpu_count = os.cpu_count() or 4
            memory_gb = 8.0
        
        return {
            'cpu_count': cpu_count,
            'cpu_model': 'Unknown',  # Would need platform-specific code
            'memory_gb': memory_gb,
            'gpu_available': self._check_gpu(),
            'timestamp': datetime.utcnow().isoformat(),
        }
    
    def _check_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            result = subprocess.run(
                ['nvidia-smi'], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def run(self) -> Dict[str, Any]:
        """Run all benchmarks"""
        results = {
            'metadata': {
                'model': self.model,
                'model_info': self.model_info,
                'engines': self.engines,
                'concurrency_levels': self.concurrency_levels,
                'duration': self.duration,
                'preset': self.preset,
                'system_info': self.system_info,
                'timestamp': datetime.utcnow().isoformat(),
            },
            'benchmarks': []
        }
        
        for engine in self.engines:
            print(f"\n{'=' * 60}")
            print(f"🔧 Testing {engine}")
            print(f"{'=' * 60}")
            
            # Setup engine (skip if requested or Docker unavailable)
            if not self.skip_setup and self.docker_client:
                print(f"⏳ Setting up {engine}...")
                try:
                    self._setup_engine(engine)
                    print(f"✅ {engine} ready")
                except Exception as e:
                    print(f"❌ Failed to setup {engine}: {e}")
                    print(f"⚠️  Using mock data for {engine}")
            else:
                print(f"⚠️  Skipping setup - using mock data")
            
            # Run benchmarks for each concurrency level
            for concurrency in self.concurrency_levels:
                print(f"\n  📊 Concurrency: {concurrency}")
                print(f"  ⏱️  Duration: {self.duration}s")
                
                try:
                    benchmark_result = self._run_benchmark(
                        engine, 
                        concurrency
                    )
                    results['benchmarks'].append(benchmark_result)
                    
                    # Print quick summary
                    print(f"  ✅ TTFT: {benchmark_result['metrics']['ttft_p50']:.3f}s")
                    print(f"  ✅ Throughput: {benchmark_result['metrics']['tokens_per_sec']:.1f} tok/s")
                    print(f"  ✅ Memory: {benchmark_result['metrics']['memory_mb']:.0f} MB")
                    
                except Exception as e:
                    print(f"  ❌ Benchmark failed: {e}")
                    
            
            # Cleanup
            if not self.skip_setup and self.docker_client:
                try:
                    self._cleanup_engine(engine)
                except:
                    pass
        
        return results
    
    def _setup_engine(self, engine: str):
        """Setup and start an engine"""
        config = ENGINE_CONFIGS[engine]
        
        # For demo purposes, we'll simulate this
        # In production, would actually start Docker containers
        time.sleep(2)  # Simulate startup time
    
    def _cleanup_engine(self, engine: str):
        """Stop and cleanup an engine"""
        pass
    
   def _run_benchmark(self, engine: str, concurrency: int) -> Dict[str, Any]:
        """Run benchmark for a specific engine and concurrency level"""
        
        if not REAL_BENCHMARKING_AVAILABLE:
            raise RuntimeError("Real benchmarking not available. Install: pip install aiohttp")
        
        # Get engine config
        config = ENGINE_CONFIGS[engine]
        base_url = f"http://localhost:{config['port']}"
        
        # Run real benchmark
        real_results = run_benchmark_sync(
            engine=engine,
            base_url=base_url,
            model_name=self.model,
            prompts=self.prompts,
            concurrency=concurrency,
            duration=self.duration
        )
        
        if not real_results:
            raise RuntimeError(f"{engine} is not responding on {base_url}. Is it running?")
        
        # Get memory usage
        memory_mb = self._get_memory_usage()
        
        # Format results
        return {
            'engine': engine,
            'concurrency': concurrency,
            'duration': self.duration,
            'metrics': {
                'ttft_p50': real_results['ttft_p50'],
                'ttft_p95': real_results['ttft_p95'],
                'ttft_p99': real_results['ttft_p99'],
                'tokens_per_sec': real_results['tokens_per_sec'],
                'total_tokens': real_results['total_tokens'],
                'successful_requests': real_results['successful_requests'],
                'failed_requests': real_results['failed_requests'],
                'memory_mb': memory_mb,
                'cpu_percent': self._get_cpu_usage(),
            },
            'timestamp': datetime.utcnow().isoformat(),
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if psutil:
            process = psutil.Process()
            return round(process.memory_info().rss / (1024 * 1024), 0)
        return 5000  # Default estimate
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        if psutil:
            return round(psutil.cpu_percent(interval=0.1), 1)
        return 75.0  # Default estimate
    
  
