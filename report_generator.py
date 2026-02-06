"""
Report generator - analyzes benchmark results and provides recommendations
"""

from typing import Dict, Any, List
import statistics


class ReportGenerator:
    """Generates reports and recommendations from benchmark results"""
    
    def __init__(self, results: Dict[str, Any]):
        self.results = results
        self.metadata = results['metadata']
        self.benchmarks = results['benchmarks']
    
    def print_summary(self):
        """Print a formatted summary of results"""
        print(f"\n{'=' * 80}")
        print(f"📊 BENCHMARK RESULTS SUMMARY")
        print(f"{'=' * 80}")
        print(f"\n🔧 Configuration:")
        print(f"  Model: {self.metadata['model']} ({self.metadata['model_info']['name']})")
        print(f"  System: {self.metadata['system_info']['cpu_count']} CPUs, "
              f"{self.metadata['system_info']['memory_gb']}GB RAM")
        if self.metadata['system_info']['gpu_available']:
            print(f"  GPU: Available")
        else:
            print(f"  GPU: Not available")
        
        # Group results by engine
        engines = {}
        for bench in self.benchmarks:
            engine = bench['engine']
            if engine not in engines:
                engines[engine] = []
            engines[engine].append(bench)
        
        # Print results table for each concurrency level
        concurrency_levels = sorted(set(b['concurrency'] for b in self.benchmarks))
        
        for concurrency in concurrency_levels:
            print(f"\n{'─' * 80}")
            print(f"Concurrency: {concurrency}")
            print(f"{'─' * 80}")
            print(f"{'Engine':<15} {'TTFT (p50)':<12} {'Throughput':<15} {'Memory':<12} {'Success Rate':<12}")
            print(f"{'─' * 80}")
            
            for engine in sorted(engines.keys()):
                bench = next((b for b in engines[engine] if b['concurrency'] == concurrency), None)
                if bench:
                    metrics = bench['metrics']
                    success_rate = (metrics['successful_requests'] / 
                                  (metrics['successful_requests'] + metrics['failed_requests'])) * 100
                    
                    print(f"{engine:<15} "
                          f"{metrics['ttft_p50']:.3f}s{'':<6} "
                          f"{metrics['tokens_per_sec']:.1f} tok/s{'':<4} "
                          f"{metrics['memory_mb']:.0f} MB{'':<5} "
                          f"{success_rate:.1f}%")
        
        print(f"{'─' * 80}")
    
    def print_recommendation(self):
        """Print recommendations based on benchmark results"""
        print(f"\n{'=' * 80}")
        print(f"💡 RECOMMENDATIONS")
        print(f"{'=' * 80}")
        
        # Analyze results
        analysis = self._analyze_results()
        
        # Determine best engine for different scenarios
        best_single = analysis['best_single_user']
        best_concurrent = analysis['best_high_concurrency']
        most_efficient = analysis['most_memory_efficient']
        
        print(f"\n🏆 Best for Single User / Low Concurrency:")
        print(f"   {best_single['engine']}")
        print(f"   • TTFT: {best_single['ttft']:.3f}s (faster response)")
        print(f"   • Throughput: {best_single['throughput']:.1f} tok/s")
        print(f"   • Memory: {best_single['memory']:.0f} MB")
        
        if len(self.metadata['concurrency_levels']) > 1:
            print(f"\n🚀 Best for High Concurrency:")
            print(f"   {best_concurrent['engine']}")
            print(f"   • Throughput: {best_concurrent['throughput']:.1f} tok/s (at {best_concurrent['concurrency']}x concurrency)")
            print(f"   • {best_concurrent['advantage']:.1f}% faster than {best_single['engine']}")
        
        print(f"\n💾 Most Memory Efficient:")
        print(f"   {most_efficient['engine']}")
        print(f"   • Memory: {most_efficient['memory']:.0f} MB")
        print(f"   • {most_efficient['savings']:.0f} MB less than {best_concurrent['engine']}")
        
        # Cost analysis (if applicable)
        if not self.metadata['system_info']['gpu_available']:
            self._print_cost_analysis(analysis)
        
        # Print specific recommendation
        print(f"\n{'─' * 80}")
        print(f"📋 Recommended Setup:")
        print(f"{'─' * 80}")
        
        use_case = self._determine_use_case()
        recommendation = self._get_recommendation(use_case, analysis)
        
        print(f"\n{recommendation['message']}\n")
        print(f"💻 Command to run:")
        print(f"   {recommendation['command']}\n")
        
        if recommendation.get('notes'):
            print(f"📝 Notes:")
            for note in recommendation['notes']:
                print(f"   • {note}")
        
        print(f"\n{'=' * 80}\n")
    
    def _analyze_results(self) -> Dict[str, Any]:
        """Analyze benchmark results to extract insights"""
        
        # Find best performers
        single_user_results = [b for b in self.benchmarks if b['concurrency'] == 1]
        high_concurrency = max(self.metadata['concurrency_levels'])
        high_concurrent_results = [b for b in self.benchmarks if b['concurrency'] == high_concurrency]
        
        # Best for single user (lowest TTFT)
        best_single = min(single_user_results, key=lambda x: x['metrics']['ttft_p50'])
        
        # Best for high concurrency (highest throughput)
        if high_concurrent_results:
            best_concurrent = max(high_concurrent_results, key=lambda x: x['metrics']['tokens_per_sec'])
            
            # Calculate advantage
            single_throughput = best_single['metrics']['tokens_per_sec']
            concurrent_throughput = best_concurrent['metrics']['tokens_per_sec']
            advantage = ((concurrent_throughput - single_throughput) / single_throughput) * 100
        else:
            best_concurrent = best_single
            advantage = 0
        
        # Most memory efficient
        most_efficient = min(self.benchmarks, key=lambda x: x['metrics']['memory_mb'])
        memory_savings = best_concurrent['metrics']['memory_mb'] - most_efficient['metrics']['memory_mb']
        
        return {
            'best_single_user': {
                'engine': best_single['engine'],
                'ttft': best_single['metrics']['ttft_p50'],
                'throughput': best_single['metrics']['tokens_per_sec'],
                'memory': best_single['metrics']['memory_mb'],
            },
            'best_high_concurrency': {
                'engine': best_concurrent['engine'],
                'concurrency': best_concurrent['concurrency'],
                'throughput': best_concurrent['metrics']['tokens_per_sec'],
                'memory': best_concurrent['metrics']['memory_mb'],
                'advantage': advantage,
            },
            'most_memory_efficient': {
                'engine': most_efficient['engine'],
                'memory': most_efficient['metrics']['memory_mb'],
                'savings': memory_savings,
            },
        }
    
    def _determine_use_case(self) -> str:
        """Determine the primary use case based on configuration"""
        if self.metadata.get('preset'):
            return self.metadata['preset']
        
        max_concurrency = max(self.metadata['concurrency_levels'])
        
        if max_concurrency <= 2:
            return 'chatbot'
        elif max_concurrency >= 20:
            return 'batch-processing'
        else:
            return 'general'
    
    def _get_recommendation(self, use_case: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific recommendation based on use case and results"""
        
        gpu_available = self.metadata['system_info']['gpu_available']
        
        if use_case == 'chatbot':
            # Recommend best single-user engine
            engine = analysis['best_single_user']['engine']
            
            if engine == 'llama.cpp':
                command = f"llama-cpp-server --model {self.metadata['model_info']['gguf_file']} --n-gpu-layers 99 --ctx-size 2048"
                message = f"✅ For chatbot workloads, {engine} provides the best latency with {analysis['best_single_user']['ttft']:.3f}s TTFT."
                notes = [
                    "Low memory footprint ideal for single-user scenarios",
                    "Works well on CPU-only systems",
                    "Consider increasing --ctx-size for longer conversations"
                ]
            elif engine == 'ollama':
                command = f"ollama run {self.metadata['model']}"
                message = f"✅ For chatbot workloads, {engine} offers the best balance of performance and ease of use."
                notes = [
                    "Simplest setup - just install and run",
                    "Good for local development",
                    "Automatic model management"
                ]
            else:  # vllm
                command = f"vllm serve {self.metadata['model_info']['hf_repo']} --host 0.0.0.0 --port 8000"
                message = f"✅ For chatbot workloads, {engine} provides excellent performance."
                notes = [
                    "Requires GPU for best performance",
                    "Higher memory usage but faster inference",
                ]
        
        elif use_case == 'batch-processing':
            # Recommend best high-concurrency engine
            engine = analysis['best_high_concurrency']['engine']
            throughput = analysis['best_high_concurrency']['throughput']
            
            if engine == 'vllm':
                command = f"vllm serve {self.metadata['model_info']['hf_repo']} --max-model-len 2048 --gpu-memory-utilization 0.9"
                message = f"✅ For high-throughput batch processing, {engine} is the clear winner with {throughput:.1f} tok/s at high concurrency."
                notes = [
                    "Best for serving multiple users simultaneously",
                    "Continuous batching optimizes GPU utilization",
                    "Requires GPU with sufficient VRAM"
                ]
            else:
                command = f"# Use {engine} with appropriate concurrency settings"
                message = f"✅ For batch processing, {engine} achieved {throughput:.1f} tok/s."
                notes = [
                    "Consider scaling horizontally for higher throughput",
                ]
        
        else:  # general use case
            # Balance between performance and efficiency
            engine = analysis['best_single_user']['engine']
            command = f"# Use {engine} for balanced performance"
            message = f"✅ For general use, {engine} offers a good balance of performance and resource usage."
            notes = []
        
        return {
            'engine': engine,
            'message': message,
            'command': command,
            'notes': notes,
        }
    
    def _print_cost_analysis(self, analysis: Dict[str, Any]):
        """Print cost analysis for cloud deployments"""
        print(f"\n💰 Estimated Cloud Costs (AWS):")
        
        # Simple cost estimation based on CPU-only instance
        instance_type = 'c6i.2xlarge'
        hourly_cost = 0.34
        
        for engine in ['llama.cpp', 'ollama', 'vllm']:
            engine_data = next((b for b in self.benchmarks 
                               if b['engine'] == engine and b['concurrency'] == 1), None)
            if engine_data:
                throughput = engine_data['metrics']['tokens_per_sec']
                # Calculate cost per 1M tokens
                seconds_per_1m = 1_000_000 / throughput
                hours_per_1m = seconds_per_1m / 3600
                cost_per_1m = hours_per_1m * hourly_cost
                
                print(f"   {engine}: ${cost_per_1m:.2f} per 1M tokens ({instance_type})")
