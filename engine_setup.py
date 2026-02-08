"""
Engine setup and model downloading
"""

import os
import subprocess
import time
from pathlib import Path
from config import SUPPORTED_MODELS, ENGINE_CONFIGS

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class EngineSetup:
    """Handles automatic engine setup and model downloading"""

    def __init__(self):
        self.models_dir = Path.home() / '.llamabench' / 'models'
        self.models_dir.mkdir(parents=True, exist_ok=True)

        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
            except:
                self.docker_client = None
        else:
            self.docker_client = None

    def setup(self, engine: str, model_id: str):
        """Setup engine and download model"""

        if model_id not in SUPPORTED_MODELS:
            raise ValueError(f"Model {model_id} not supported")

        model_info = SUPPORTED_MODELS[model_id]

        if engine == 'llama.cpp':
            self._setup_llamacpp(model_info)
        elif engine == 'ollama':
            self._setup_ollama(model_info)
        else:
            raise ValueError(f"Engine {engine} not supported")

    def _setup_llamacpp(self, model_info):
        """Setup llama.cpp"""

        # Download GGUF model
        print(f"📥 Downloading {model_info['gguf_file']}...")
        model_path = self._download_gguf(model_info)

        if not self.docker_client:
            print("⚠️  Docker not available, skipping container start")
            print(f"Model downloaded to: {model_path}")
            return

        # Stop existing container
        try:
            container = self.docker_client.containers.get(
                'llamabench-llamacpp')
            print("🛑 Stopping existing container...")
            container.stop()
            container.remove()
        except:
            pass

        # Start llama.cpp server
        print("🚀 Starting llama.cpp server...")
        container = self.docker_client.containers.run(
            'ghcr.io/ggerganov/llama.cpp:server',
            name='llamabench-llamacpp',
            ports={'8080/tcp': 8080},
            volumes={str(self.models_dir): {'bind': '/models', 'mode': 'ro'}},
            command=[
                '--model', f'/models/{model_info["gguf_file"]}',
                '--host', '0.0.0.0',
                '--port', '8080',
                '--n-gpu-layers', '99',
                '--ctx-size', '2048'
            ],
            detach=True,
            remove=True
        )

        # Wait for health check
        print("⏳ Waiting for server to start...")
        time.sleep(5)

        # Verify
        import requests
        try:
            response = requests.get('http://localhost:8080/health', timeout=5)
            if response.status_code == 200:
                print("✅ llama.cpp server running on http://localhost:8080")
            else:
                raise Exception("Health check failed")
        except:
            raise Exception("Server didn't start properly")

    def _setup_ollama(self, model_info):
        """Setup Ollama"""

        # Check if Ollama installed
        try:
            subprocess.run(['ollama', '--version'],
                           capture_output=True, check=True)
            print("✅ Ollama already installed")
        except:
            print("📥 Installing Ollama...")
            subprocess.run(
                'curl -fsSL https://ollama.com/install.sh | sh',
                shell=True,
                check=True
            )

        # Pull model
        print(f"📥 Pulling {model_info['name']}...")

        # Map our model names to Ollama names
        ollama_model_map = {
            'llama-3.1-8b': 'llama3.1',
            'mistral-7b': 'mistral',
            'qwen-2.5-7b': 'qwen2.5:7b'
        }

        ollama_model = ollama_model_map.get(model_info.get('id'), 'llama3.1')

        result = subprocess.run(
            ['ollama', 'pull', ollama_model],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Failed to pull model: {result.stderr}")

        print(f"✅ Ollama ready with {ollama_model}")

    def _download_gguf(self, model_info):
        """Download GGUF model from HuggingFace"""

        model_path = self.models_dir / model_info['gguf_file']

        if model_path.exists():
            print(f"✅ Model already downloaded: {model_path}")
            return model_path

        # Try importing huggingface_hub directly
        try:
            from huggingface_hub import hf_hub_download

            print(f"Downloading from {model_info['gguf_repo']}...")
            downloaded_path = hf_hub_download(
                repo_id=model_info['gguf_repo'],
                filename=model_info['gguf_file'],
                local_dir=str(self.models_dir),
                local_dir_use_symlinks=False
            )
            print(f"✅ Downloaded to: {downloaded_path}")
            return Path(downloaded_path)

        except ImportError:
            print("⚠️  huggingface_hub not installed")
            print("Install with: pip install huggingface_hub")
            raise Exception("huggingface_hub required for model download")
