# Quick Start Guide

## Installation

### Option 1: Quick Setup
```bash
git clone https://github.com/yourusername/llamabench.git
cd llamabench
./setup.sh
```

### Option 2: Manual Setup
```bash
git clone https://github.com/yourusername/llamabench.git
cd llamabench
pip install -r requirements.txt
chmod +x llamabench.py
```

## Your First Benchmark

### 1. List Available Models
```bash
python llamabench.py list-models
```

### 2. Run a Simple Benchmark
```bash
# Compare llama.cpp and Ollama for Llama 3.1 8B
python llamabench.py run \
  --model llama-3.1-8b \
  --engines llama.cpp,ollama \
  --concurrency 1,5,10
```

This will:
- Download/setup both engines (if Docker is available)
- Run benchmarks at 1, 5, and 10 concurrent requests
- Test for 60 seconds at each concurrency level
- Generate a recommendation

### 3. View Results
Results are saved to `benchmark_results.json` by default. To re-analyze:
```bash
python llamabench.py compare benchmark_results.json
```

## Common Scenarios

### Chatbot Application
You're building a chatbot that serves 1-5 users at a time:
```bash
python llamabench.py run \
  --model llama-3.1-8b \
  --preset chatbot
```

This tests:
- Low concurrency (1-5 users)
- Optimizes for response latency
- Uses conversational prompts

**Expected output**: Recommendation for lowest TTFT engine

### Batch Processing
You need to process large volumes of requests:
```bash
python llamabench.py run \
  --model mistral-7b \
  --preset batch-processing
```

This tests:
- High concurrency (10-50 requests)
- Optimizes for total throughput
- Uses short, varied prompts

**Expected output**: Recommendation for highest throughput engine

### Edge Device / Resource-Constrained
You're deploying on a device with limited memory:
```bash
python llamabench.py run \
  --model qwen-2.5-7b \
  --preset edge-device
```

This tests:
- Single user
- Memory-constrained scenarios
- CPU-only performance

**Expected output**: Recommendation for lowest memory usage

## Advanced Usage

### Custom Concurrency Levels
```bash
python llamabench.py run \
  --model llama-3.1-8b \
  --engines llama.cpp,vllm \
  --concurrency 1,2,3,5,8,13,21  # Fibonacci sequence
```

### Custom Test Duration
```bash
# Run for 5 minutes per test for more accuracy
python llamabench.py run \
  --model mistral-7b \
  --duration 300
```

### Custom Prompts
Test with your actual use case:
```bash
python llamabench.py run \
  --model llama-3.1-8b \
  --prompt "Translate the following Python code to Rust: [your code]"
```

### Save to Specific File
```bash
python llamabench.py run \
  --model llama-3.1-8b \
  --output my_benchmark_$(date +%Y%m%d).json
```

### Compare Multiple Runs
```bash
# Run benchmark 1
python llamabench.py run --model llama-3.1-8b --output run1.json

# Run benchmark 2 (after optimization)
python llamabench.py run --model llama-3.1-8b --output run2.json

# Compare
python llamabench.py compare run1.json
python llamabench.py compare run2.json
```

## Using Docker Compose

### Start All Engines
```bash
docker-compose up -d
```

### Run Benchmark Against Running Engines
```bash
python llamabench.py run \
  --model llama-3.1-8b \
  --engines llama.cpp,ollama,vllm \
  --skip-setup
```

### Stop Engines
```bash
docker-compose down
```

## Understanding Output

### Metrics Explained

**TTFT (Time to First Token)**
- Time until first token is generated
- Lower is better for interactive applications
- p50 = median, p95 = 95th percentile, p99 = 99th percentile

**Throughput**
- Tokens generated per second across all concurrent requests
- Higher is better for batch processing
- Scales with concurrency

**Memory**
- Peak memory usage during benchmark
- Important for deployment planning
- Includes model weights + runtime overhead

**Success Rate**
- Percentage of requests that completed successfully
- Should be 99%+ for production use
- Lower might indicate overload

### Reading the Recommendation

The tool provides specific recommendations:
```
🏆 Best for Single User / Low Concurrency:
   llama.cpp
   • TTFT: 0.148s (faster response)
   • Throughput: 45.2 tok/s
   • Memory: 4823 MB
```

This means:
- Use llama.cpp if latency matters most
- It's fastest to first token
- Uses least memory
- Good for chat, interactive use

```
🚀 Best for High Concurrency:
   vllm
   • Throughput: 337.8 tok/s (at 10x concurrency)
   • 150.2% faster than llama.cpp
```

This means:
- Use vLLM for serving many users
- Much higher total throughput
- Better GPU utilization
- Good for API serving, batch jobs

## Troubleshooting

### Docker Not Available
If you see "Docker not available", the tool will use simulated data for demo purposes. To run real benchmarks:
1. Install Docker: https://docs.docker.com/get-docker/
2. Ensure Docker daemon is running
3. Run benchmark again

### Out of Memory
If benchmarks fail with OOM:
- Reduce `--concurrency` values
- Use a smaller model
- Check available RAM with `free -h`

### Slow Performance
If benchmarks are slower than expected:
- Check CPU usage: `top`
- Verify GPU is being used: `nvidia-smi`
- Ensure no other heavy processes are running
- Try reducing `--concurrency`

### Engine Won't Start
If a specific engine fails:
- Check Docker logs: `docker logs llamabench-{engine}`
- Verify Docker image exists: `docker images`
- Check port availability: `netstat -tulpn | grep {port}`

## Next Steps

1. **Run your first benchmark** with a preset
2. **Share results** - open an issue with your benchmark data
3. **Contribute** - see CONTRIBUTING.md
4. **Blog about it** - help spread the word
5. **Star the repo** - if you find it useful!

## Getting Help

- Open an issue: https://github.com/yourusername/llamabench/issues
- Discussions: https://github.com/yourusername/llamabench/discussions
- Read the full docs: https://github.com/yourusername/llamabench/blob/main/README.md
