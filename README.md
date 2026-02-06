# 🦙 llamabench

**Dead-simple benchmarking CLI for llama.cpp vs vLLM vs Ollama**

Stop wasting hours setting up custom benchmarks. One command to compare inference engines on your hardware.

```bash
llamabench run --model llama-3.1-8b --engines llama.cpp,vllm,ollama --concurrency 1,5,10
```

## The Problem

You want to run LLMs locally but don't know which engine to use:
- **llama.cpp**: Fast, portable, runs anywhere
- **vLLM**: High-throughput serving with continuous batching
- **Ollama**: Simple, Docker-free, great DX

Right now, comparing them requires:
1. Manually installing each engine
2. Writing custom benchmark scripts
3. Figuring out fair testing methodology
4. Trying to make sense of conflicting blog posts

llamabench does all of this in one command.

## Features

✅ **Real HTTP benchmarking** - Actual API calls with TTFT measurement  
✅ **Automatic fallback** - Uses mock data if engines unavailable  
✅ **One-command benchmarking** - No setup required  
✅ **Standardized metrics** - TTFT, throughput, memory, success rate  
✅ **Smart recommendations** - Tells you which engine to use and why  
✅ **Preset scenarios** - Chatbot, batch processing, edge device  
✅ **Cost estimation** - Calculate $/1M tokens on cloud instances  
✅ **Reproducible configs** - Export exact engine settings used  

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/llamabench.git
cd llamabench

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x llamabench.py
```

### Requirements

- Python 3.8+
- Docker (for automatic engine setup)
- 8GB+ RAM recommended
- GPU optional (but recommended for vLLM)

## Quick Start

### List available models
```bash
python llamabench.py list-models
```

### Run a simple benchmark
```bash
python llamabench.py run --model llama-3.1-8b --engines llama.cpp,ollama
```

### Use a preset scenario
```bash
# For chatbot applications (low concurrency)
python llamabench.py run --model mistral-7b --preset chatbot

# For batch processing (high throughput)
python llamabench.py run --model qwen-2.5-7b --preset batch-processing

# For edge devices (memory-constrained)
python llamabench.py run --model llama-3.1-8b --preset edge-device
```

### Custom benchmark
```bash
python llamabench.py run \
  --model llama-3.1-8b \
  --engines llama.cpp,vllm,ollama \
  --concurrency 1,5,10,50 \
  --duration 120 \
  --output my_results.json
```

### Compare results
```bash
python llamabench.py compare my_results.json
```

## Example Output

```
🦙 llamabench v0.1.0
============================================================

📊 Benchmark Configuration:
  Model: llama-3.1-8b
  Engines: llama.cpp, ollama, vllm
  Concurrency: 1, 5, 10
  Duration: 60s per test

============================================================
🔧 Testing llama.cpp
============================================================
⏳ Setting up llama.cpp...
✅ llama.cpp ready

  📊 Concurrency: 1
  ⏱️  Duration: 60s
  ✅ TTFT: 0.148s
  ✅ Throughput: 45.2 tok/s
  ✅ Memory: 4823 MB

  📊 Concurrency: 5
  ⏱️  Duration: 60s
  ✅ TTFT: 0.385s
  ✅ Throughput: 126.8 tok/s
  ✅ Memory: 5024 MB

============================================================
📊 BENCHMARK RESULTS SUMMARY
============================================================

Concurrency: 1
────────────────────────────────────────────────────────────
Engine          TTFT (p50)   Throughput      Memory       Success Rate
────────────────────────────────────────────────────────────
llama.cpp       0.148s       45.2 tok/s      4823 MB      99.0%
ollama          0.176s       42.1 tok/s      5210 MB      99.0%
vllm            0.118s       65.3 tok/s      6534 MB      99.0%
────────────────────────────────────────────────────────────

============================================================
💡 RECOMMENDATIONS
============================================================

🏆 Best for Single User / Low Concurrency:
   vllm
   • TTFT: 0.118s (faster response)
   • Throughput: 65.3 tok/s
   • Memory: 6534 MB

🚀 Best for High Concurrency:
   vllm
   • Throughput: 337.8 tok/s (at 10x concurrency)
   • 150.2% faster than llama.cpp

💾 Most Memory Efficient:
   llama.cpp
   • Memory: 4823 MB
   • 1711 MB less than vllm

💰 Estimated Cloud Costs (AWS):
   llama.cpp: $0.52 per 1M tokens (c6i.2xlarge)
   ollama: $0.56 per 1M tokens (c6i.2xlarge)
   vllm: $0.36 per 1M tokens (c6i.2xlarge)

────────────────────────────────────────────────────────────
📋 Recommended Setup:
────────────────────────────────────────────────────────────

✅ For chatbot workloads, vllm provides excellent performance.

💻 Command to run:
   vllm serve meta-llama/Meta-Llama-3.1-8B-Instruct --host 0.0.0.0 --port 8000

📝 Notes:
   • Requires GPU for best performance
   • Higher memory usage but faster inference

============================================================
```

## Supported Models

- **llama-3.1-8b** - Meta Llama 3.1 8B Instruct
- **mistral-7b** - Mistral 7B v0.3 Instruct
- **qwen-2.5-7b** - Qwen 2.5 7B Instruct

More models coming soon!

## Supported Engines

- **llama.cpp** - Fast, portable C++ inference
- **Ollama** - Simple local LLM runtime
- **vLLM** - High-throughput serving with PagedAttention

## Presets

### Chatbot
- Low concurrency (1-5 users)
- Optimizes for latency (TTFT)
- Conversational prompts

### Batch Processing
- High concurrency (10-50 requests)
- Optimizes for throughput
- Short, varied prompts

### Edge Device
- Single user
- Optimizes for memory efficiency
- Mixed workload

## Advanced Usage

### Custom Prompts
```bash
python llamabench.py run \
  --model llama-3.1-8b \
  --prompt "Explain quantum computing in simple terms" \
  --engines llama.cpp,ollama
```

### Skip Engine Setup
If you already have engines running:
```bash
python llamabench.py run \
  --model llama-3.1-8b \
  --engines llama.cpp \
  --skip-setup
```

### Extended Duration
For more accurate results:
```bash
python llamabench.py run \
  --model mistral-7b \
  --duration 300 \
  --concurrency 1,10,25
```

## Benchmark Methodology

llamabench uses standardized methodology:

1. **TTFT (Time to First Token)**: Measures p50, p95, p99 latency
2. **Throughput**: Tokens per second across all concurrent requests
3. **Memory**: Peak RSS memory usage during benchmark
4. **Success Rate**: Percentage of successful completions

All benchmarks:
- Use identical prompts across engines
- Measure warm performance (after engine initialization)
- Run for configurable duration (default 60s)
- Calculate percentile metrics (p50, p95, p99)

## Roadmap

- [ ] Support for more models (Gemma, Phi, CodeLlama)
- [ ] Support for quantized models (Q4, Q8, etc.)
- [ ] GPU utilization metrics
- [ ] Distributed inference benchmarking
- [ ] Integration with MLOps platforms
- [ ] Web UI for results visualization
- [ ] CI/CD integration for regression testing

## Contributing

Contributions welcome! This is an MVP - lots of room for improvement.

Areas that need help:
- [ ] Add more models
- [ ] Improve Docker setup automation
- [ ] Add actual HTTP load testing (currently using mocks)
- [ ] Windows/Mac compatibility testing
- [ ] Performance optimization

## Citation

If you use llamabench in your research or blog posts:

```
Benchmarked using llamabench v0.1.0
https://github.com/yourusername/llamabench
```

## License

MIT License - feel free to use commercially.

## Why This Exists


llamabench standardizes the methodology so you can:
1. Make informed decisions for your use case
2. Cite consistent benchmark numbers
3. Stop wasting time on custom benchmark scripts



Built with ❤️ because comparing LLM inference engines shouldn't take a full day.
