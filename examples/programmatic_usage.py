#!/usr/bin/env python3
"""
Example: Using llamabench programmatically

This shows how to integrate llamabench into your own scripts
for automated testing and CI/CD.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark_runner import BenchmarkRunner
from report_generator import ReportGenerator


def run_automated_benchmark():
    """
    Run a benchmark and automatically select the best engine
    based on your requirements
    """
    
    print("🤖 Running automated benchmark...")
    
    # Define your requirements
    model = 'llama-3.1-8b'
    max_concurrency = 5  # Expected peak concurrent users
    target_use_case = 'chatbot'  # or 'batch-processing', 'edge-device'
    
    # Run benchmark
    runner = BenchmarkRunner(
        model=model,
        engines=['llama.cpp', 'ollama', 'vllm'],
        concurrency_levels=[1, max_concurrency],
        duration=30,  # Shorter for demo
        preset=target_use_case,
        skip_setup=True  # Set to False if you want auto-setup
    )
    
    results = runner.run()
    
    # Analyze results
    generator = ReportGenerator(results)
    
    # Get programmatic recommendation
    analysis = generator._analyze_results()
    best_engine = analysis['best_single_user']['engine']
    best_ttft = analysis['best_single_user']['ttft']
    
    print(f"\n✅ Recommendation: Use {best_engine}")
    print(f"   TTFT: {best_ttft:.3f}s")
    
    # Save configuration for deployment
    deployment_config = {
        'model': model,
        'engine': best_engine,
        'ttft': best_ttft,
        'use_case': target_use_case,
        'timestamp': results['metadata']['timestamp']
    }
    
    with open('deployment_config.json', 'w') as f:
        json.dump(deployment_config, f, indent=2)
    
    print(f"\n📝 Deployment config saved to: deployment_config.json")
    
    return best_engine


def compare_models():
    """
    Compare different models to see which performs best
    """
    
    print("🔬 Comparing models...")
    
    models = ['llama-3.1-8b', 'mistral-7b', 'qwen-2.5-7b']
    results_by_model = {}
    
    for model in models:
        print(f"\nTesting {model}...")
        
        runner = BenchmarkRunner(
            model=model,
            engines=['llama.cpp'],  # Test with single engine
            concurrency_levels=[1],
            duration=30,
            skip_setup=True
        )
        
        results = runner.run()
        
        # Extract key metric
        benchmark = results['benchmarks'][0]
        results_by_model[model] = {
            'ttft': benchmark['metrics']['ttft_p50'],
            'throughput': benchmark['metrics']['tokens_per_sec'],
            'memory': benchmark['metrics']['memory_mb']
        }
    
    # Find best
    best_model = min(results_by_model.items(), 
                     key=lambda x: x[1]['ttft'])
    
    print(f"\n{'=' * 60}")
    print("Model Comparison Results")
    print(f"{'=' * 60}")
    
    for model, metrics in results_by_model.items():
        print(f"\n{model}:")
        print(f"  TTFT: {metrics['ttft']:.3f}s")
        print(f"  Throughput: {metrics['throughput']:.1f} tok/s")
        print(f"  Memory: {metrics['memory']:.0f} MB")
    
    print(f"\n🏆 Winner: {best_model[0]}")
    
    return best_model[0]


def check_regression(baseline_file: str, current_file: str, threshold: float = 10.0):
    """
    Check if current benchmark shows regression vs baseline
    
    Args:
        baseline_file: Path to baseline results
        current_file: Path to current results
        threshold: Percentage threshold for regression (default 10%)
    
    Returns:
        bool: True if no regression, False if regression detected
    """
    
    print(f"📊 Checking for performance regression...")
    print(f"   Baseline: {baseline_file}")
    print(f"   Current: {current_file}")
    print(f"   Threshold: {threshold}%")
    
    # Load results
    with open(baseline_file) as f:
        baseline = json.load(f)
    
    with open(current_file) as f:
        current = json.load(f)
    
    # Compare metrics for same engine/concurrency
    regressions = []
    
    for curr_bench in current['benchmarks']:
        # Find matching baseline benchmark
        baseline_bench = next(
            (b for b in baseline['benchmarks'] 
             if b['engine'] == curr_bench['engine'] 
             and b['concurrency'] == curr_bench['concurrency']),
            None
        )
        
        if not baseline_bench:
            continue
        
        # Check TTFT regression
        baseline_ttft = baseline_bench['metrics']['ttft_p50']
        current_ttft = curr_bench['metrics']['ttft_p50']
        ttft_change = ((current_ttft - baseline_ttft) / baseline_ttft) * 100
        
        # Check throughput regression
        baseline_throughput = baseline_bench['metrics']['tokens_per_sec']
        current_throughput = curr_bench['metrics']['tokens_per_sec']
        throughput_change = ((current_throughput - baseline_throughput) / baseline_throughput) * 100
        
        print(f"\n{curr_bench['engine']} (concurrency {curr_bench['concurrency']}):")
        print(f"  TTFT: {ttft_change:+.1f}%")
        print(f"  Throughput: {throughput_change:+.1f}%")
        
        if ttft_change > threshold:
            regressions.append(f"{curr_bench['engine']}: TTFT degraded by {ttft_change:.1f}%")
        
        if throughput_change < -threshold:
            regressions.append(f"{curr_bench['engine']}: Throughput degraded by {abs(throughput_change):.1f}%")
    
    if regressions:
        print(f"\n❌ Performance regression detected:")
        for regression in regressions:
            print(f"   • {regression}")
        return False
    else:
        print(f"\n✅ No significant performance regression")
        return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='llamabench examples')
    parser.add_argument('--example', choices=['automated', 'compare', 'regression'], 
                       default='automated',
                       help='Which example to run')
    parser.add_argument('--baseline', help='Baseline results file for regression check')
    parser.add_argument('--current', help='Current results file for regression check')
    
    args = parser.parse_args()
    
    if args.example == 'automated':
        run_automated_benchmark()
    elif args.example == 'compare':
        compare_models()
    elif args.example == 'regression':
        if not args.baseline or not args.current:
            print("Error: --baseline and --current required for regression check")
            sys.exit(1)
        passed = check_regression(args.baseline, args.current)
        sys.exit(0 if passed else 1)
