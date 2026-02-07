"""
Configuration for llamabench
"""

# Supported models with their metadata
SUPPORTED_MODELS = {
    'llama-3.1-8b': {
        'id': 'llama-3.1-8b',
        'name': 'Llama 3.1 8B',
        'size': '8B',
        'hf_repo': 'meta-llama/Meta-Llama-3.1-8B-Instruct',
        'gguf_repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
        'gguf_file': 'Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf',
        'context_length': 8192,
        'recommended_memory_gb': 6,
    },
    'mistral-7b': {
        'id': 'mistral-7b',
        'name': 'Mistral 7B v0.3',
        'size': '7B',
        'hf_repo': 'mistralai/Mistral-7B-Instruct-v0.3',
        'gguf_repo': 'bartowski/Mistral-7B-Instruct-v0.3-GGUF',
        'gguf_file': 'Mistral-7B-Instruct-v0.3-Q4_K_M.gguf',
        'context_length': 8192,
        'recommended_memory_gb': 5,
    },
    'qwen-2.5-7b': {
        'id': 'qwen-2.5-7b',
        'name': 'Qwen 2.5 7B',
        'size': '7B',
        'hf_repo': 'Qwen/Qwen2.5-7B-Instruct',
        'gguf_repo': 'bartowski/Qwen2.5-7B-Instruct-GGUF',
        'gguf_file': 'Qwen2.5-7B-Instruct-Q4_K_M.gguf',
        'context_length': 32768,
        'recommended_memory_gb': 5,
    },
}

# Supported engines
SUPPORTED_ENGINES = ['llama.cpp', 'ollama', 'vllm']

# Engine configurations
ENGINE_CONFIGS = {
    'llama.cpp': {
        'docker_image': 'ghcr.io/ggerganov/llama.cpp:server',
        'port': 8080,
        'health_endpoint': '/health',
        'completion_endpoint': '/completion',
        'default_args': [
            '--host', '0.0.0.0',
            '--port', '8080',
            '--n-gpu-layers', '99',  # Use GPU if available
            '--ctx-size', '2048',
        ],
    },
    'ollama': {
        'docker_image': 'ollama/ollama:latest',
        'port': 11434,
        'health_endpoint': '/api/tags',
        'completion_endpoint': '/api/generate',
        'model_prefix': '',  # Ollama uses model names directly
    },
    'vllm': {
        'docker_image': 'vllm/vllm-openai:latest',
        'port': 8000,
        'health_endpoint': '/health',
        'completion_endpoint': '/v1/completions',
        'default_args': [
            '--host', '0.0.0.0',
            '--port', '8000',
            '--gpu-memory-utilization', '0.9',
        ],
    },
}

# Preset configurations
PRESETS = {
    'chatbot': {
        'description': 'Low concurrency, conversational workload',
        'concurrency': [1, 2, 5],
        'duration': 60,
        'prompt_style': 'conversational',
    },
    'batch-processing': {
        'description': 'High throughput, batch processing',
        'concurrency': [10, 25, 50],
        'duration': 120,
        'prompt_style': 'short',
    },
    'edge-device': {
        'description': 'Memory-constrained, single-user',
        'concurrency': [1],
        'duration': 60,
        'prompt_style': 'mixed',
    },
}

# Standard benchmark prompts
BENCHMARK_PROMPTS = {
    'conversational': [
        "Explain quantum computing to a 10-year-old.",
        "What are the pros and cons of remote work?",
        "Write a creative story about a time-traveling cat.",
        "Explain the difference between supervised and unsupervised learning.",
        "What would happen if humans could photosynthesize?",
    ],
    'short': [
        "List 5 programming languages.",
        "What is the capital of France?",
        "Define machine learning.",
        "Name 3 types of clouds.",
        "What is 15 * 23?",
    ],
    'mixed': [
        "Explain quantum computing to a 10-year-old.",
        "What is the capital of France?",
        "Write a creative story about a time-traveling cat.",
        "Define machine learning.",
        "What are the pros and cons of remote work?",
    ],
}

# Default benchmark prompt
DEFAULT_PROMPT = "Explain the concept of neural networks and how they work in modern AI systems. Include examples of applications."

# Cloud instance pricing ($/hour) - rough estimates
CLOUD_PRICING = {
    'aws': {
        'c6i.2xlarge': 0.34,  # 8 vCPU, 16GB RAM (CPU-only)
        'g5.xlarge': 1.006,   # 4 vCPU, 16GB RAM, 1x A10G GPU
        'g5.2xlarge': 1.212,  # 8 vCPU, 32GB RAM, 1x A10G GPU
    },
    'gcp': {
        'n2-standard-8': 0.38,  # 8 vCPU, 32GB RAM (CPU-only)
        'g2-standard-4': 0.89,  # 4 vCPU, 16GB RAM, 1x L4 GPU
    },
}
