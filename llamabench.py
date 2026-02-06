#!/usr/bin/env python3
"""
llamabench - Dead-simple benchmarking CLI for llama.cpp vs vLLM vs Ollama

Usage:
    llamabench run --model llama-3.1-8b --engines llama.cpp,vllm,ollama --concurrency 1,5,10
    llamabench compare results.json
    llamabench list-models
"""

import argparse
import sys
import json
from pathlib import Path

from benchmark_runner import BenchmarkRunner
from report_generator import ReportGenerator
from config import SUPPORTED_MODELS, SUPPORTED_ENGINES


def main():
    parser = argparse.ArgumentParser(
        description="llamabench - Benchmark llama.cpp, vLLM, and Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run benchmark command
    run_parser = subparsers.add_parser('run', help='Run benchmarks')
    run_parser.add_argument(
        '--model',
        required=True,
        help='Model to benchmark (e.g., llama-3.1-8b, mistral-7b)'
    )
    run_parser.add_argument(
        '--engines',
        default='llama.cpp,ollama',
        help='Comma-separated list of engines to test (default: llama.cpp,ollama)'
    )
    run_parser.add_argument(
        '--concurrency',
        default='1,5,10',
        help='Comma-separated concurrency levels to test (default: 1,5,10)'
    )
    run_parser.add_argument(
        '--preset',
        choices=['chatbot', 'batch-processing', 'edge-device'],
        help='Use a preset configuration for common scenarios'
    )
    run_parser.add_argument(
        '--prompt',
        help='Custom prompt to use for testing (default: standard benchmark prompt)'
    )
    run_parser.add_argument(
        '--output',
        default='benchmark_results.json',
        help='Output file for results (default: benchmark_results.json)'
    )
    run_parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duration of each benchmark in seconds (default: 60)'
    )
    run_parser.add_argument(
        '--skip-setup',
        action='store_true',
        help='Skip engine setup (assumes engines are already running)'
    )
    
    # List models command
    list_parser = subparsers.add_parser('list-models', help='List supported models')
    
    # Compare results command
    compare_parser = subparsers.add_parser('compare', help='Compare benchmark results')
    compare_parser.add_argument(
        'results_file',
        help='Path to benchmark results JSON file'
    )
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_benchmark(args)
    elif args.command == 'list-models':
        list_models()
    elif args.command == 'compare':
        compare_results(args)
    else:
        parser.print_help()
        sys.exit(1)


def run_benchmark(args):
    """Run the benchmark suite"""
    print(f"🦙 llamabench v0.1.0")
    print(f"{'=' * 60}")
    
    # Validate model
    if args.model not in SUPPORTED_MODELS:
        print(f"❌ Error: Model '{args.model}' not supported")
        print(f"Supported models: {', '.join(SUPPORTED_MODELS.keys())}")
        sys.exit(1)
    
    # Parse engines
    engines = [e.strip() for e in args.engines.split(',')]
    for engine in engines:
        if engine not in SUPPORTED_ENGINES:
            print(f"❌ Error: Engine '{engine}' not supported")
            print(f"Supported engines: {', '.join(SUPPORTED_ENGINES)}")
            sys.exit(1)
    
    # Parse concurrency levels
    try:
        concurrency_levels = [int(c.strip()) for c in args.concurrency.split(',')]
    except ValueError:
        print(f"❌ Error: Invalid concurrency levels")
        sys.exit(1)
    
    print(f"\n📊 Benchmark Configuration:")
    print(f"  Model: {args.model}")
    print(f"  Engines: {', '.join(engines)}")
    print(f"  Concurrency: {', '.join(map(str, concurrency_levels))}")
    print(f"  Duration: {args.duration}s per test")
    if args.preset:
        print(f"  Preset: {args.preset}")
    print()
    
    # Run benchmarks
    runner = BenchmarkRunner(
        model=args.model,
        engines=engines,
        concurrency_levels=concurrency_levels,
        duration=args.duration,
        preset=args.preset,
        custom_prompt=args.prompt,
        skip_setup=args.skip_setup
    )
    
    try:
        results = runner.run()
        
        # Save results
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_path}")
        
        # Generate report
        generator = ReportGenerator(results)
        generator.print_summary()
        generator.print_recommendation()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def list_models():
    """List all supported models"""
    print("📋 Supported Models:\n")
    for model_id, model_info in SUPPORTED_MODELS.items():
        print(f"  • {model_id}")
        print(f"    Name: {model_info['name']}")
        print(f"    Size: {model_info['size']}")
        print(f"    HuggingFace: {model_info['hf_repo']}")
        print()


def compare_results(args):
    """Compare benchmark results from a file"""
    results_path = Path(args.results_file)
    
    if not results_path.exists():
        print(f"❌ Error: Results file not found: {results_path}")
        sys.exit(1)
    
    with open(results_path) as f:
        results = json.load(f)
    
    generator = ReportGenerator(results)
    generator.print_summary()
    generator.print_recommendation()


if __name__ == '__main__':
    main()
