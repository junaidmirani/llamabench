#!/usr/bin/env python3
"""
Visualize benchmark results as charts

Usage:
    python scripts/visualize.py benchmark_results.json
"""

import json
import sys
from pathlib import Path


def create_ascii_chart(data, title, max_width=60):
    """Create a simple ASCII bar chart"""
    
    print(f"\n{title}")
    print("=" * max_width)
    
    # Find max value for scaling
    max_val = max(item['value'] for item in data)
    
    for item in data:
        label = item['label']
        value = item['value']
        unit = item.get('unit', '')
        
        # Calculate bar width
        bar_width = int((value / max_val) * (max_width - 25))
        bar = '█' * bar_width
        
        # Format value
        if isinstance(value, float):
            value_str = f"{value:.2f}"
        else:
            value_str = str(value)
        
        print(f"{label:<15} {bar} {value_str} {unit}")
    
    print()


def visualize_results(results_file):
    """Generate ASCII visualizations from benchmark results"""
    
    print(f"📊 Visualizing: {results_file}")
    
    with open(results_file) as f:
        results = json.load(f)
    
    benchmarks = results['benchmarks']
    
    # Group by concurrency level
    concurrency_levels = sorted(set(b['concurrency'] for b in benchmarks))
    
    for concurrency in concurrency_levels:
        print(f"\n{'#' * 70}")
        print(f"# Concurrency: {concurrency}")
        print(f"{'#' * 70}")
        
        level_benchmarks = [b for b in benchmarks if b['concurrency'] == concurrency]
        
        # TTFT chart
        ttft_data = [
            {
                'label': b['engine'],
                'value': b['metrics']['ttft_p50'],
                'unit': 's'
            }
            for b in level_benchmarks
        ]
        ttft_data.sort(key=lambda x: x['value'])  # Lower is better
        create_ascii_chart(ttft_data, "Time to First Token (lower is better)", max_width=60)
        
        # Throughput chart
        throughput_data = [
            {
                'label': b['engine'],
                'value': b['metrics']['tokens_per_sec'],
                'unit': 'tok/s'
            }
            for b in level_benchmarks
        ]
        throughput_data.sort(key=lambda x: x['value'], reverse=True)  # Higher is better
        create_ascii_chart(throughput_data, "Throughput (higher is better)", max_width=60)
        
        # Memory chart
        memory_data = [
            {
                'label': b['engine'],
                'value': b['metrics']['memory_mb'],
                'unit': 'MB'
            }
            for b in level_benchmarks
        ]
        memory_data.sort(key=lambda x: x['value'])  # Lower is better
        create_ascii_chart(memory_data, "Memory Usage (lower is better)", max_width=60)
    
    # Scalability chart - show how throughput scales with concurrency
    print(f"\n{'#' * 70}")
    print(f"# Throughput Scalability")
    print(f"{'#' * 70}")
    
    engines = sorted(set(b['engine'] for b in benchmarks))
    
    for engine in engines:
        print(f"\n{engine}:")
        engine_data = [
            {
                'label': f"  {b['concurrency']}x",
                'value': b['metrics']['tokens_per_sec'],
                'unit': 'tok/s'
            }
            for b in benchmarks if b['engine'] == engine
        ]
        engine_data.sort(key=lambda x: int(x['label'].strip().replace('x', '')))
        
        for item in engine_data:
            bar_width = int((item['value'] / 500) * 40)  # Scale to reasonable width
            bar = '█' * bar_width
            print(f"{item['label']:<8} {bar} {item['value']:.1f} {item['unit']}")


def create_markdown_table(results_file):
    """Create a markdown table for easy sharing"""
    
    with open(results_file) as f:
        results = json.load(f)
    
    benchmarks = results['benchmarks']
    model = results['metadata']['model']
    
    print(f"\n## Benchmark Results: {model}\n")
    print("| Engine | Concurrency | TTFT (p50) | Throughput | Memory | Success Rate |")
    print("|--------|-------------|------------|------------|--------|--------------|")
    
    for bench in sorted(benchmarks, key=lambda x: (x['concurrency'], x['engine'])):
        metrics = bench['metrics']
        success_rate = (metrics['successful_requests'] / 
                       (metrics['successful_requests'] + metrics['failed_requests'])) * 100
        
        print(f"| {bench['engine']:<10} | "
              f"{bench['concurrency']:<11} | "
              f"{metrics['ttft_p50']:.3f}s | "
              f"{metrics['tokens_per_sec']:.1f} tok/s | "
              f"{metrics['memory_mb']:.0f} MB | "
              f"{success_rate:.1f}% |")
    
    print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/visualize.py <results.json>")
        print("   or: python scripts/visualize.py <results.json> --markdown")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    if not Path(results_file).exists():
        print(f"Error: File not found: {results_file}")
        sys.exit(1)
    
    if len(sys.argv) > 2 and sys.argv[2] == '--markdown':
        create_markdown_table(results_file)
    else:
        visualize_results(results_file)
