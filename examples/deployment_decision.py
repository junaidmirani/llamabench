#!/usr/bin/env python3
"""
Example: Automated Deployment Decision

This example shows how a team could use llamabench to make
data-driven decisions about which inference engine to deploy.

Scenario:
You're deploying a customer support chatbot that needs to:
- Handle 1-10 concurrent users
- Respond quickly (low latency matters)
- Run on AWS within budget constraints
- Support fallback to CPU if GPU unavailable
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark_runner import BenchmarkRunner
from report_generator import ReportGenerator


def deployment_decision_workflow():
    """
    Complete workflow for making a deployment decision
    """
    
    print("=" * 70)
    print("🚀 AUTOMATED DEPLOYMENT DECISION WORKFLOW")
    print("=" * 70)
    
    # Step 1: Define requirements
    print("\n📋 Step 1: Requirements")
    print("-" * 70)
    
    requirements = {
        'use_case': 'customer_support_chatbot',
        'max_concurrent_users': 10,
        'target_latency_ms': 200,  # 200ms to first token
        'budget_per_month': 500,  # USD
        'gpu_available': False,  # Assume CPU-only for cost
    }
    
    for key, value in requirements.items():
        print(f"  {key}: {value}")
    
    # Step 2: Run benchmark
    print("\n📊 Step 2: Running benchmarks...")
    print("-" * 70)
    
    runner = BenchmarkRunner(
        model='llama-3.1-8b',
        engines=['llama.cpp', 'ollama'],  # Skip vLLM (GPU-only)
        concurrency_levels=[1, 5, 10],
        duration=60,
        preset='chatbot',
        skip_setup=True  # Using mock data for demo
    )
    
    results = runner.run()
    
    # Step 3: Analyze results
    print("\n🔍 Step 3: Analyzing results...")
    print("-" * 70)
    
    generator = ReportGenerator(results)
    analysis = generator._analyze_results()
    
    # Step 4: Check requirements
    print("\n✅ Step 4: Requirement validation")
    print("-" * 70)
    
    best_engine = analysis['best_single_user']['engine']
    best_ttft_ms = analysis['best_single_user']['ttft'] * 1000
    best_memory_gb = analysis['best_single_user']['memory'] / 1024
    
    # Latency check
    latency_ok = best_ttft_ms <= requirements['target_latency_ms']
    print(f"  Latency requirement ({requirements['target_latency_ms']}ms):")
    print(f"    Best: {best_ttft_ms:.0f}ms ({best_engine})")
    print(f"    Status: {'✅ PASS' if latency_ok else '❌ FAIL'}")
    
    # Budget check (simplified)
    instance_type = 'c6i.2xlarge'  # 8 vCPU, 16GB RAM
    hourly_rate = 0.34
    monthly_cost = hourly_rate * 24 * 30
    
    budget_ok = monthly_cost <= requirements['budget_per_month']
    print(f"  Budget requirement (${requirements['budget_per_month']}/month):")
    print(f"    Estimated cost: ${monthly_cost:.0f}/month ({instance_type})")
    print(f"    Status: {'✅ PASS' if budget_ok else '❌ FAIL'}")
    
    # Memory check (does it fit on instance?)
    instance_memory_gb = 16
    memory_ok = best_memory_gb <= instance_memory_gb * 0.8  # Leave 20% headroom
    print(f"  Memory requirement ({instance_memory_gb}GB instance):")
    print(f"    Model memory: {best_memory_gb:.1f}GB")
    print(f"    Status: {'✅ PASS' if memory_ok else '❌ FAIL'}")
    
    # Step 5: Generate deployment config
    print("\n🎯 Step 5: Deployment recommendation")
    print("-" * 70)
    
    if latency_ok and budget_ok and memory_ok:
        print(f"  ✅ APPROVED: Deploy with {best_engine}")
        print(f"\n  Recommended Configuration:")
        print(f"    Engine: {best_engine}")
        print(f"    Model: llama-3.1-8b")
        print(f"    Instance: AWS {instance_type}")
        print(f"    Expected TTFT: {best_ttft_ms:.0f}ms")
        print(f"    Monthly cost: ${monthly_cost:.0f}")
        
        # Generate Terraform/deployment config
        deployment_config = {
            'engine': best_engine,
            'model': 'llama-3.1-8b',
            'cloud': {
                'provider': 'aws',
                'instance_type': instance_type,
                'monthly_cost_usd': monthly_cost
            },
            'performance': {
                'ttft_ms': best_ttft_ms,
                'throughput_tok_s': analysis['best_single_user']['throughput'],
                'memory_gb': best_memory_gb
            },
            'requirements_met': {
                'latency': latency_ok,
                'budget': budget_ok,
                'memory': memory_ok
            }
        }
        
        # Save config
        config_path = Path('deployment_config.json')
        with open(config_path, 'w') as f:
            json.dump(deployment_config, f, indent=2)
        
        print(f"\n  📝 Configuration saved to: {config_path}")
        
        # Generate deployment commands
        print(f"\n  🚀 Quick deploy:")
        if best_engine == 'llama.cpp':
            print(f"    docker run -d -p 8080:8080 \\")
            print(f"      ghcr.io/ggerganov/llama.cpp:server \\")
            print(f"      --model llama-3.1-8b.gguf \\")
            print(f"      --host 0.0.0.0 --port 8080")
        elif best_engine == 'ollama':
            print(f"    docker run -d -p 11434:11434 \\")
            print(f"      ollama/ollama:latest")
            print(f"    docker exec ollama ollama run llama3.1:8b")
        
    else:
        print(f"  ❌ REJECTED: Requirements not met")
        print(f"\n  Issues:")
        if not latency_ok:
            print(f"    • Latency too high: {best_ttft_ms:.0f}ms > {requirements['target_latency_ms']}ms")
            print(f"      → Consider: GPU instance, smaller model, or relax requirement")
        if not budget_ok:
            print(f"    • Cost too high: ${monthly_cost:.0f} > ${requirements['budget_per_month']}")
            print(f"      → Consider: Reserved instances, spot instances, or smaller instance")
        if not memory_ok:
            print(f"    • Memory too high: {best_memory_gb:.1f}GB doesn't fit on {instance_memory_gb}GB")
            print(f"      → Consider: Larger instance or quantized model")
    
    print("\n" + "=" * 70)
    
    return deployment_config if (latency_ok and budget_ok and memory_ok) else None


def compare_cloud_providers():
    """
    Compare costs across cloud providers
    """
    
    print("\n☁️  Cloud Provider Comparison")
    print("=" * 70)
    
    # Load results
    with open('deployment_config.json') as f:
        config = json.load(f)
    
    memory_gb = config['performance']['memory_gb']
    
    # Instance options
    providers = {
        'AWS': {
            'c6i.2xlarge': {'cpu': 8, 'ram': 16, 'cost': 0.34},
            'c6i.4xlarge': {'cpu': 16, 'ram': 32, 'cost': 0.68},
            'g5.xlarge': {'cpu': 4, 'ram': 16, 'gpu': '1x A10G', 'cost': 1.006},
        },
        'GCP': {
            'n2-standard-8': {'cpu': 8, 'ram': 32, 'cost': 0.38},
            'n2-standard-16': {'cpu': 16, 'ram': 64, 'cost': 0.76},
            'g2-standard-4': {'cpu': 4, 'ram': 16, 'gpu': '1x L4', 'cost': 0.89},
        },
        'Azure': {
            'F8s_v2': {'cpu': 8, 'ram': 16, 'cost': 0.34},
            'F16s_v2': {'cpu': 16, 'ram': 32, 'cost': 0.68},
        }
    }
    
    print(f"\nRequired memory: {memory_gb:.1f}GB")
    print(f"\n{'Provider':<10} {'Instance':<20} {'Specs':<30} {'$/hour':<10} {'$/month':<10}")
    print("-" * 80)
    
    recommendations = []
    
    for provider, instances in providers.items():
        for instance_name, specs in instances.items():
            # Check if instance has enough memory
            if specs['ram'] >= memory_gb * 1.2:  # 20% headroom
                monthly = specs['cost'] * 24 * 30
                
                spec_str = f"{specs['cpu']} CPU, {specs['ram']}GB RAM"
                if 'gpu' in specs:
                    spec_str += f", {specs['gpu']}"
                
                print(f"{provider:<10} {instance_name:<20} {spec_str:<30} "
                      f"${specs['cost']:<9.3f} ${monthly:<9.0f}")
                
                recommendations.append({
                    'provider': provider,
                    'instance': instance_name,
                    'monthly_cost': monthly,
                    'has_gpu': 'gpu' in specs
                })
    
    # Show cheapest option
    cpu_only = [r for r in recommendations if not r['has_gpu']]
    if cpu_only:
        cheapest = min(cpu_only, key=lambda x: x['monthly_cost'])
        print(f"\n💰 Cheapest CPU-only: {cheapest['provider']} {cheapest['instance']} "
              f"(${cheapest['monthly_cost']:.0f}/month)")
    
    print()


if __name__ == '__main__':
    config = deployment_decision_workflow()
    
    if config:
        compare_cloud_providers()
