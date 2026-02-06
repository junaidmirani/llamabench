# Real Benchmarking Implementation

This document explains the real HTTP benchmarking implementation that replaces the mock data.

## Overview

The real benchmarking system (`real_benchmark.py`) implements:
- ✅ Actual HTTP requests to inference engines
- ✅ TTFT (Time to First Token) measurement with streaming
- ✅ Throughput calculation (tokens/sec)
- ✅ Concurrent request handling
- ✅ Success/failure tracking
- ✅ Percentile metrics (p50, p95, p99)

## Architecture

### Components

1. **RealBenchmarkEngine** (`real_benchmark.py`)
   - Handles HTTP communication with inference engines
   - Measures TTFT by detecting first chunk in streaming response
   - Tracks token count and timing
   - Supports concurrent workers

2. **Integration** (`benchmark_runner.py`)
   - Automatically uses real benchmarking if available
   - Falls back to mock data if engine not accessible
   - Collects memory and CPU metrics

3. **Mock Server** (`scripts/mock_server.py`)
   - Testing server that simulates engine behavior
   - Useful for development without real engines

## Quick Start

### Option 1: Test with Mock Server (Easiest)

```bash
# Terminal 1: Start mock server
python scripts/mock_server.py

# Terminal 2: Run benchmark
python llamabench.py run --model llama-3.1-8b --engines llama.cpp
```

### Option 2: Test with Real llama.cpp

```bash
# Start llama.cpp server
docker run -d -p 8080:8080 \
  ghcr.io/ggerganov/llama.cpp:server \
  --model /path/to/model.gguf \
  --host 0.0.0.0 --port 8080

# Run benchmark
python llamabench.py run --model llama-3.1-8b --engines llama.cpp
```

### Option 3: Test with Ollama

```bash
# Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1

# Run benchmark
python llamabench.py run --model llama-3.1-8b --engines ollama
```

## How It Works

### TTFT Measurement

```python
start_time = time.perf_counter()

async with session.post(url, json=payload) as response:
    async for line in response.content:
        if line:  # First chunk received
            ttft = time.perf_counter() - start_time
            # Got time to first token!
            break
```

### Concurrent Load Testing

```python
async def worker(worker_id):
    """Each worker sends requests until duration expires"""
    while time.time() - start_time < duration:
        result = await measure_single_request(prompt)
        results.append(result)

# Launch N concurrent workers
workers = [asyncio.create_task(worker(i)) for i in range(concurrency)]
await asyncio.gather(*workers)
```

### Throughput Calculation

```python
# Aggregate all successful requests
total_tokens = sum(r['tokens'] for r in successful_requests)
tokens_per_sec = total_tokens / duration
```

## API Endpoints by Engine

### llama.cpp
```python
POST http://localhost:8080/completion
{
  "prompt": "Your prompt here",
  "n_predict": 512,
  "temperature": 0.7,
  "stream": true
}
```

### Ollama
```python
POST http://localhost:11434/api/generate
{
  "model": "llama3.1",
  "prompt": "Your prompt here",
  "stream": true
}
```

### vLLM
```python
POST http://localhost:8000/v1/completions
{
  "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
  "prompt": "Your prompt here",
  "max_tokens": 512,
  "temperature": 0.7
}
```

## Testing the Implementation

### Unit Test
```bash
python test_real_benchmark.py
```

### With Specific Engine
```bash
# Test llama.cpp (default)
python test_real_benchmark.py

# Test all engines
python test_real_benchmark.py --all
```

### Integration Test
```bash
# Full benchmark with real data
python llamabench.py run \
  --model llama-3.1-8b \
  --engines llama.cpp,ollama \
  --concurrency 1,5 \
  --duration 30
```

## Metrics Explained

### TTFT (Time to First Token)
- **p50**: Median time - 50% of requests faster than this
- **p95**: 95th percentile - 95% of requests faster
- **p99**: 99th percentile - only 1% slower

Lower is better. Critical for interactive applications.

### Throughput (tokens/sec)
- Total tokens generated across all concurrent requests
- Divided by benchmark duration
- Higher is better

### Success Rate
- Percentage of requests that completed successfully
- Should be >99% for production workloads
- Lower indicates overload or errors

## Real Data vs Mock Data

The benchmark runner automatically detects if it can connect to engines:

```python
if REAL_BENCHMARKING_AVAILABLE:
    # Try to connect and get real data
    real_results = run_benchmark_sync(...)
    if real_results:
        return format_real_results(real_results)

# Fallback to mock data
return generate_mock_result(...)
```

Results include a `real_data: true` flag when using actual benchmarks.

## Common Issues

### "Connection refused"
```bash
# Check if engine is running
curl http://localhost:8080/health  # llama.cpp
curl http://localhost:11434/api/tags  # Ollama
```

### "Timeout errors"
- Engine may be overloaded
- Try reducing concurrency: `--concurrency 1,2,5`
- Try shorter duration: `--duration 30`

### "Module not found: aiohttp"
```bash
pip install aiohttp
# or
pip install -r requirements.txt
```

### "Mock data being used"
This is expected if:
- Engine not running on expected port
- Docker not started
- Network issue

Check the output - it will say "⚠️ falling back to mock data"

## Advanced Usage

### Custom Endpoints

Edit `ENGINE_CONFIGS` in `config.py`:

```python
ENGINE_CONFIGS['custom-engine'] = {
    'port': 9999,
    'health_endpoint': '/health',
    'completion_endpoint': '/custom/completion',
}
```

### Custom Prompts

```bash
python llamabench.py run \
  --model llama-3.1-8b \
  --prompt "Your specific prompt here" \
  --engines llama.cpp
```

### Different Port

Edit `config.py` or start engine on expected port:

```bash
# llama.cpp: 8080
# Ollama: 11434
# vLLM: 8000
```

## Performance Considerations

### Memory Overhead
- Each concurrent request uses ~10-50MB
- aiohttp session pool is reused
- Memory tracked separately via psutil

### CPU Usage
- Async I/O is non-blocking
- Can handle 100+ concurrent requests
- Limited by engine, not client

### Network
- All requests to localhost by default
- No data leaves your machine
- Bandwidth not a concern for local testing

## Next Steps

1. **Test with Mock Server**: `python scripts/mock_server.py`
2. **Test Real Engine**: Start llama.cpp/Ollama
3. **Run Full Benchmark**: Compare all engines
4. **Analyze Results**: Check TTFT and throughput
5. **Deploy Best Engine**: Use recommendation

## Limitations

Current implementation:
- ✅ Supports streaming (TTFT measurement)
- ✅ Handles concurrent requests
- ✅ Tracks success/failure
- ⚠️ Token counting is approximate (counts chunks, not actual tokens)
- ⚠️ GPU metrics not yet implemented
- ⚠️ Distributed benchmarking not supported

Future improvements:
- [ ] Proper token counting with tokenizer
- [ ] GPU memory and utilization tracking
- [ ] Multi-node distributed testing
- [ ] Custom metric collectors
- [ ] Result comparison over time

## Contributing

To improve the real benchmarking:

1. Add more engine support in `real_benchmark.py`
2. Improve token counting accuracy
3. Add GPU metrics collection
4. Better error handling for edge cases
5. Add regression tests

See `CONTRIBUTING.md` for details.
