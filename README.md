
# llamabench

> **Production-grade benchmarking for LLM inference engines**  
> Compare llama.cpp, vLLM, and Ollama with real HTTP load testing and microsecond-precision TTFT measurement.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

```bash
# One command to benchmark any model on any engine
llamabench setup --engine llama.cpp --model llama-3.1-8b
llamabench run --model llama-3.1-8b --engines llama.cpp --concurrency 1,10,50
```



## Why llamabench?

Every "llama.cpp vs vLLM" article uses different hardware, models, and metrics. **llamabench standardizes inference benchmarking** so you can:

- Make data-driven deployment decisions
- Compare apples-to-apples across engines
- Cite reproducible benchmark numbers
- Validate performance claims

**Built for ML engineers shipping real systems, not blog posts.**

---

## Features

| Feature | Status |
|---------|--------|
| Real HTTP benchmarking with streaming TTFT | ✅ |
| Async concurrent load testing (aiohttp) | ✅ |
| Percentile latency metrics (p50/p95/p99) | ✅ |
| Auto-download models from HuggingFace | ✅ |
| Auto-start inference engines (Docker) | ✅ |
| Multi-engine comparison | ✅ |
| JSON export for CI/CD | ✅ |
| Cost estimation (AWS/GCP) | ✅ |
| GPU metrics | 🚧 |
| Distributed benchmarking | 🚧 |

---

## Quick Start

### Installation

```bash
git clone https://github.com/yourusername/llamabench.git
cd llamabench
pip install -r requirements.txt
```

**Requirements:** Python 3.8+, Docker, 8GB+ RAM

### Setup Engine + Model

```bash
# Downloads model and starts llama.cpp server
llamabench setup --engine llama.cpp --model llama-3.1-8b

# Or use Ollama (auto-installs if needed)
llamabench setup --engine ollama --model llama-3.1-8b
```

### Run Benchmark

```bash
llamabench run --model llama-3.1-8b --engines llama.cpp --concurrency 1,5,10
```

---

## Example Output

```
🦙 llamabench v0.2.0

📊 Benchmark Configuration
  Model:       llama-3.1-8b (Meta Llama 3.1 8B Instruct)
  Engine:      llama.cpp
  Concurrency: 1, 5, 10
  Duration:    60s per test

════════════════════════════════════════════════════════════════════════════════
🔧 llama.cpp @ http://localhost:8080
════════════════════════════════════════════════════════════════════════════════

  Concurrency: 1
  ────────────────────────────────────────────────────────────────────────────
  TTFT (p50):        142ms
  TTFT (p95):        198ms
  TTFT (p99):        234ms
  Throughput:        47.3 tok/s
  Success rate:      100.0% (1,247 requests)
  Memory:            4,821 MB
  
  Concurrency: 10
  ────────────────────────────────────────────────────────────────────────────
  TTFT (p50):        389ms
  TTFT (p95):        612ms
  TTFT (p99):        891ms
  Throughput:        203.4 tok/s
  Success rate:      99.8% (12,389 requests)
  Memory:            7,104 MB

════════════════════════════════════════════════════════════════════════════════
💡 RECOMMENDATION
════════════════════════════════════════════════════════════════════════════════

✅ Deploy llama.cpp for this workload

  • TTFT: 142ms (p50) - suitable for interactive use
  • Throughput: 203 tok/s at 10x concurrency
  • Memory: 4.8GB - fits on c6i.2xlarge ($0.34/hr)
  • Cost: ~$0.48/1M tokens

  Command:
  docker run -p 8080:8080 ghcr.io/ggerganov/llama.cpp:server \
    --model llama-3.1-8b-q4.gguf --ctx-size 2048

  Estimated AWS cost: $245/month (continuous operation)
```

---

## Supported Engines

| Engine | Status | Notes |
|--------|--------|-------|
| **llama.cpp** | ✅ | CPU/GPU, GGUF quantization |
| **Ollama** | ✅ | Auto-install, multi-model |
| **vLLM** | ✅ | GPU-only, PagedAttention |
| TensorRT-LLM | 🚧 | Planned |
| SGLang | 🚧 | Planned |

## Supported Models

Pre-configured models (auto-download):

- `llama-3.1-8b` - Meta Llama 3.1 8B Instruct
- `mistral-7b` - Mistral 7B v0.3 Instruct
- `qwen-2.5-7b` - Qwen 2.5 7B Instruct

Custom models: Use any HuggingFace repo (GGUF or native format)

---

## Advanced Usage

### Custom Benchmarks

```bash
# Test specific concurrency levels with custom duration
llamabench run \
  --model llama-3.1-8b \
  --engines llama.cpp,vllm \
  --concurrency 1,2,5,10,25,50 \
  --duration 300 \
  --output production-benchmark.json
```

### Preset Scenarios

```bash
# Chatbot workload (optimizes for latency)
llamabench run --preset chatbot --model mistral-7b

# Batch processing (optimizes for throughput)
llamabench run --preset batch-processing --model qwen-2.5-7b

# Edge deployment (memory-constrained)
llamabench run --preset edge-device --model llama-3.1-8b
```

### Skip Auto-Setup

```bash
# Use existing running engines
llamabench run --model llama-3.1-8b --engines llama.cpp --skip-setup
```

### Visualization

```bash
# Generate comparison charts
python scripts/visualize.py benchmark_results.json

# Export markdown table
python scripts/visualize.py benchmark_results.json --markdown
```

---

## Methodology

llamabench measures real-world performance using:

**TTFT (Time to First Token)**
- Detects first byte in streaming HTTP response
- Reports p50, p95, p99 percentiles
- Accounts for network + inference latency

**Throughput**
- Total tokens generated / benchmark duration
- Measured across all concurrent requests
- Includes successful requests only

**Success Rate**
- HTTP 200 responses / total requests
- Excludes timeouts and errors
- Target: >99% for production workloads

**All benchmarks:**
- Use identical prompts across engines
- Run after engine warmup (discard first 10 requests)
- Measure sustained performance over 60s default duration
- Track memory via `psutil` process monitoring

---

## Architecture

```
llamabench/
├── llamabench.py          # CLI entry point
├── real_benchmark.py      # Async HTTP benchmarking engine
├── benchmark_runner.py    # Orchestration and metrics
├── engine_setup.py        # Auto-download and Docker management
├── report_generator.py    # Analysis and recommendations
└── config.py              # Model and engine configurations
```

**Key dependencies:**
- `aiohttp` - Async HTTP for concurrent requests
- `docker` - Container orchestration
- `psutil` - System metrics
- `huggingface_hub` - Model downloading

---

## CI/CD Integration

Use llamabench for regression testing:

```yaml
# .github/workflows/benchmark.yml
- name: Benchmark
  run: |
    llamabench setup --engine llama.cpp --model llama-3.1-8b
    llamabench run --output current.json --duration 60
    python scripts/check_regression.py baseline.json current.json
```

See [.github/workflows/benchmark.yml](.github/workflows/benchmark.yml) for full example.

---

## Roadmap

**v0.3 (Next)**
- [ ] GPU utilization metrics (nvidia-ml-py)
- [ ] Proper token counting with tokenizers
- [ ] TensorRT-LLM support
- [ ] Batch size optimization

**v0.4**
- [ ] Web UI dashboard
- [ ] Historical tracking (SQLite)
- [ ] Multi-GPU benchmarking
- [ ] Prometheus metrics export

**v1.0**
- [ ] Distributed inference testing
- [ ] Auto-tuning recommendations
- [ ] Cost optimization engine
- [ ] Production SLA validation

See [ROADMAP.md](ROADMAP.md) for full list.

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

**High-priority items:**
- GPU metrics implementation
- Windows/macOS testing
- Additional engine support (TensorRT-LLM, SGLang)
- Quantization comparison framework

---

## Citation

```bibtex
@software{llamabench2025,
  title = {llamabench: Production-grade LLM inference benchmarking},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/llamabench}
}
```

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Acknowledgments

Built with insights from:
- [llama.cpp](https://github.com/ggerganov/llama.cpp) community
- [vLLM](https://github.com/vllm-project/vllm) benchmarking methodology
- [Ollama](https://github.com/ollama/ollama) ease-of-use principles

**Not affiliated with Meta, Anthropic, or any model providers.**
```
