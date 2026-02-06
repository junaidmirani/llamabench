# llamabench Project Structure

```
llamabench/
├── llamabench.py              # Main CLI entry point
├── benchmark_runner.py        # Core benchmarking logic
├── report_generator.py        # Results analysis and recommendations
├── config.py                  # Configuration (models, engines, presets)
│
├── requirements.txt           # Python dependencies
├── setup.sh                   # Installation script
│
├── README.md                  # Main documentation
├── QUICKSTART.md              # Quick start guide
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # MIT License
├── .gitignore                 # Git ignore rules
│
├── docker-compose.yml         # Docker orchestration for engines
│
├── .github/
│   └── workflows/
│       └── benchmark.yml      # CI/CD workflow
│
├── scripts/
│   ├── visualize.py          # Visualization utilities
│   └── check_regression.py   # (TODO) Regression testing
│
├── examples/
│   └── programmatic_usage.py # Example Python integration
│
├── docs/                      # (TODO) Additional documentation
│   ├── methodology.md        # Benchmarking methodology
│   └── api.md                # Programmatic API docs
│
└── tests/                     # (TODO) Unit tests
    ├── test_benchmark.py
    └── test_config.py
```

## Core Components

### llamabench.py
Main CLI interface. Handles argument parsing and orchestrates benchmark runs.

**Key functions:**
- `run_benchmark()` - Execute benchmark suite
- `list_models()` - Display supported models
- `compare_results()` - Analyze saved results

### benchmark_runner.py
Core benchmarking engine that runs tests across different engines and concurrency levels.

**Key class: BenchmarkRunner**
- Manages engine setup/teardown
- Executes load tests
- Collects metrics (TTFT, throughput, memory)
- Handles Docker orchestration (when available)

### report_generator.py
Analyzes benchmark results and generates recommendations.

**Key class: ReportGenerator**
- Formats results tables
- Identifies best performers
- Generates use-case recommendations
- Estimates cloud costs

### config.py
Central configuration for:
- Supported models and their metadata
- Engine configurations and Docker images
- Preset scenarios (chatbot, batch-processing, edge-device)
- Standard benchmark prompts

## Usage Examples

### CLI
```bash
# Simple benchmark
python llamabench.py run --model llama-3.1-8b --engines llama.cpp,ollama

# With preset
python llamabench.py run --model mistral-7b --preset chatbot

# Custom configuration
python llamabench.py run \
  --model qwen-2.5-7b \
  --engines llama.cpp,vllm \
  --concurrency 1,5,10,25 \
  --duration 120 \
  --output results.json
```

### Programmatic
```python
from benchmark_runner import BenchmarkRunner
from report_generator import ReportGenerator

# Run benchmark
runner = BenchmarkRunner(
    model='llama-3.1-8b',
    engines=['llama.cpp', 'ollama'],
    concurrency_levels=[1, 5, 10],
    duration=60
)
results = runner.run()

# Analyze
generator = ReportGenerator(results)
generator.print_summary()
generator.print_recommendation()
```

## Docker Setup

### Manual Start
```bash
# Start all engines
docker-compose up -d

# Run benchmark against running engines
python llamabench.py run --model llama-3.1-8b --skip-setup

# Stop engines
docker-compose down
```

### Automatic (Default)
llamabench automatically starts and stops engines if Docker is available.

## Output Format

Results are saved as JSON:

```json
{
  "metadata": {
    "model": "llama-3.1-8b",
    "engines": ["llama.cpp", "ollama", "vllm"],
    "concurrency_levels": [1, 5, 10],
    "system_info": {...}
  },
  "benchmarks": [
    {
      "engine": "llama.cpp",
      "concurrency": 1,
      "metrics": {
        "ttft_p50": 0.148,
        "ttft_p95": 0.192,
        "ttft_p99": 0.222,
        "tokens_per_sec": 45.2,
        "memory_mb": 4823,
        "successful_requests": 1980,
        "failed_requests": 20
      }
    }
  ]
}
```

## Extending llamabench

### Adding a New Model

Edit `config.py`:
```python
SUPPORTED_MODELS['new-model-id'] = {
    'name': 'Display Name',
    'size': '7B',
    'hf_repo': 'org/model-name',
    'gguf_repo': 'org/model-gguf',
    'gguf_file': 'model-q4.gguf',
    'context_length': 8192,
    'recommended_memory_gb': 5,
}
```

### Adding a New Engine

Edit `config.py`:
```python
ENGINE_CONFIGS['new-engine'] = {
    'docker_image': 'engine/image:tag',
    'port': 8080,
    'health_endpoint': '/health',
    'completion_endpoint': '/v1/completions',
    'default_args': [...]
}
```

Then update `SUPPORTED_ENGINES` list.

### Adding a New Preset

Edit `config.py`:
```python
PRESETS['new-preset'] = {
    'description': 'Use case description',
    'concurrency': [1, 5, 10],
    'duration': 60,
    'prompt_style': 'conversational',
}
```

## Development

### Local Testing
```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests (when implemented)
pytest tests/

# Run linter
flake8 .

# Format code
black .
```

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

### v0.2 - Real Benchmarking
- [ ] Actual HTTP load testing (replace mocks)
- [ ] Docker container automation
- [ ] GPU metrics collection
- [ ] More models (Gemma, Phi-3, CodeLlama)

### v0.3 - Advanced Features
- [ ] Quantization comparison (Q4 vs Q5 vs Q8)
- [ ] Custom model support
- [ ] Distributed inference benchmarking
- [ ] Web UI for visualization

### v0.4 - Production Ready
- [ ] Comprehensive test suite
- [ ] CI/CD regression testing
- [ ] Historical trend tracking
- [ ] Export to various formats (CSV, HTML, PDF)

### v1.0 - Industry Standard
- [ ] Integration with MLOps platforms
- [ ] Certification/badge program
- [ ] Public leaderboard
- [ ] Professional support offering

## License

MIT - See [LICENSE](LICENSE) file for details.
